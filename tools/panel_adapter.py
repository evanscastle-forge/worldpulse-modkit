#!/usr/bin/env python3
"""panel_adapter: connect any tool-calling model to the WorldPulse agent panel (docs/panel-protocol.md).

Reads the panel's JSON lines on stdin, runs the model with AGENTS.md as its instructions and a small
set of tools (list, read and write files, run modkit), and writes the panel's JSON lines on stdout.
Python 3.8+, standard library only.

  WORLDPULSE_LLM_API    openai (any OpenAI-compatible endpoint: OpenAI, OpenRouter, Ollama, LM Studio,
                        llama.cpp) or anthropic
  WORLDPULSE_LLM_URL    base URL (default https://api.openai.com/v1 or https://api.anthropic.com)
  WORLDPULSE_LLM_MODEL  model name (default for anthropic: claude-opus-5-5)
  WORLDPULSE_LLM_KEY    API key (else OPENAI_API_KEY / ANTHROPIC_API_KEY); local servers need none

  python3 tools/panel_adapter.py --mod furhats            # panel JSON lines on stdin/stdout
  python3 tools/panel_adapter.py --mod furhats --chat     # plain text, for trying it in a terminal
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_STEPS = 24
MAX_READ = 40000
RUNNABLE = {"validate", "test", "sprite", "new-def", "override", "new", "doctor"}

TOOLS = [
    {"name": "list_files", "description": "List files under a folder of the toolkit (default: the mod).",
     "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "folder, relative to the toolkit root"}}}},
    {"name": "read_file", "description": "Read a text file of the toolkit (docs, reference/core, the mod).",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write a whole file inside the mod folder (mods/<mod>/...). Replaces it if it exists.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "modkit", "description": "Run python3 tools/modkit.py with these arguments, e.g. 'validate furhats'. "
                                      "Allowed: validate, test, sprite, new-def, override, new, doctor.",
     "parameters": {"type": "object", "properties": {"args": {"type": "string"}}, "required": ["args"]}},
]


def system_prompt(mod):
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    return (agents + "\n\n## This session\n\nYou are connected through panel_adapter.py. The mod you are working on is "
            "`%s` (folder `mods/%s`). Your tools: list_files, read_file, write_file (only inside the mod folder), and "
            "modkit (runs tools/modkit.py). Read files before you change them; validate after every change." % (mod, mod))


class Workspace:
    def __init__(self, mod):
        self.mod = mod
        self.mod_dir = (ROOT / "mods" / mod).resolve()

    def inside(self, path, base):
        p = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
        try:
            p.relative_to(base)
        except ValueError:
            return None
        return p

    def run(self, name, args):
        try:
            if name == "list_files":
                base = self.inside(args.get("path") or "mods/%s" % self.mod, ROOT)
                if base is None or not base.is_dir():
                    return "no such folder", True
                files = [p.relative_to(ROOT).as_posix() for p in sorted(base.rglob("*")) if p.is_file() and ".git" not in p.parts]
                return "\n".join(files[:400]) or "(empty)", False
            if name == "read_file":
                p = self.inside(args["path"], ROOT)
                if p is None or not p.is_file():
                    return "no such file: %s" % args["path"], True
                text = p.read_text(encoding="utf-8", errors="replace")
                return text if len(text) <= MAX_READ else text[:MAX_READ] + "\n... (cut at %d characters)" % MAX_READ, False
            if name == "write_file":
                p = self.inside(args["path"], self.mod_dir)
                if p is None:
                    return "refused: you may only write inside mods/%s/" % self.mod, True
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(args["content"], encoding="utf-8")
                return "wrote %s (%d characters)" % (p.relative_to(ROOT).as_posix(), len(args["content"])), False
            if name == "modkit":
                argv = shlex.split(args.get("args", ""))
                if not argv or argv[0] not in RUNNABLE:
                    return "refused: allowed modkit commands are %s" % ", ".join(sorted(RUNNABLE)), True
                if argv[0] == "sprite" and "--plain" not in argv:
                    argv.append("--plain")
                r = subprocess.run([sys.executable, str(ROOT / "tools" / "modkit.py")] + argv, capture_output=True, text=True, cwd=str(ROOT), timeout=600)
                out = (r.stdout + r.stderr).strip()
                return (out[-MAX_READ:] or "(no output)") + "\n(exit %d)" % r.returncode, False
            return "unknown tool %s" % name, True
        except (OSError, KeyError, ValueError, subprocess.SubprocessError) as e:
            return "failed: %s" % e, True


def post(url, headers, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=dict(headers, **{"content-type": "application/json"}))
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %d from %s: %s" % (e.code, url, e.read().decode("utf-8", "replace")[:500]))
    except urllib.error.URLError as e:
        raise RuntimeError("cannot reach %s: %s" % (url, e.reason))


class OpenAI:
    """Any OpenAI-compatible /chat/completions endpoint with function calling."""

    def __init__(self, url, model, key, system):
        self.url = (url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        self.model = model or "gpt-4o-mini"
        self.headers = {"authorization": "Bearer " + key} if key else {}
        self.messages = [{"role": "system", "content": system}]
        self.tools = [{"type": "function", "function": t} for t in TOOLS]

    def user(self, text):
        self.messages.append({"role": "user", "content": text})

    def step(self):
        """One model call: (text, [(id, name, args)])."""
        r = post(self.url, self.headers, {"model": self.model, "messages": self.messages, "tools": self.tools})
        msg = r["choices"][0]["message"]
        self.messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
        calls = []
        for c in msg.get("tool_calls") or []:
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except ValueError:
                args = None
            calls.append((c["id"], c["function"]["name"], args))
        return msg.get("content") or "", calls

    def results(self, results):
        for call_id, text, _ in results:
            self.messages.append({"role": "tool", "tool_call_id": call_id, "content": text})


class Anthropic:
    """The Claude Messages API (raw HTTP)."""

    def __init__(self, url, model, key, system):
        self.url = (url or "https://api.anthropic.com").rstrip("/") + "/v1/messages"
        self.model = model or "claude-opus-5-5"
        self.headers = {"anthropic-version": "2023-06-01"}
        if key:
            self.headers["x-api-key"] = key
        if self.model in ("claude-opus-5-5", "claude-sonnet-5-5", "claude-opus-5", "claude-fable-5-1"):
            # A safety decline re-runs on a fallback model inside the same call.
            self.headers["anthropic-beta"] = "server-side-fallback-2026-07-01"
        self.system = system
        self.messages = []
        self.tools = [{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]} for t in TOOLS]

    def user(self, text):
        self.messages.append({"role": "user", "content": text})

    def step(self):
        body = {"model": self.model, "max_tokens": 16000, "system": self.system, "messages": self.messages, "tools": self.tools}
        if "anthropic-beta" in self.headers:
            body["fallbacks"] = "default"
        r = post(self.url, self.headers, body)
        content = r.get("content") or []
        self.messages.append({"role": "assistant", "content": content})  # whole content, thinking blocks included
        if r.get("stop_reason") == "refusal":
            return "(the model declined this request)", []
        text = "\n".join(b.get("text", "") for b in content if b.get("type") == "text")
        calls = [(b["id"], b["name"], b.get("input")) for b in content if b.get("type") == "tool_use"]
        return text, calls

    def results(self, results):
        self.messages.append({"role": "user", "content": [
            dict({"type": "tool_result", "tool_use_id": call_id, "content": text}, **({"is_error": True} if err else {}))
            for call_id, text, err in results]})


def emit(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def turn(model, workspace, text, chat):
    model.user(text)
    for _ in range(MAX_STEPS):
        reply, calls = model.step()
        if reply.strip():
            if chat:
                print(reply.strip())
            else:
                emit({"type": "assistant", "message": {"content": [{"type": "text", "text": reply}]}})
        if not calls:
            return reply, False
        results = []
        for call_id, name, args in calls:
            if args is None:
                results.append((call_id, "the arguments were not valid JSON; send them again", True))
                continue
            detail = args.get("args") or args.get("path") or ""
            if chat:
                print("  [%s %s]" % (name, detail))
            else:
                emit({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": {"command": detail}}]}})
            out, err = workspace.run(name, args)
            results.append((call_id, out, err))
        model.results(results)
    return "stopped after %d steps" % MAX_STEPS, True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], epilog="\n".join(__doc__.split("\n")[5:]),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mod", required=True, help="the mod id to work on (mods/<id>)")
    p.add_argument("--chat", action="store_true", help="plain text in and out instead of panel JSON lines")
    p.add_argument("--api", default=os.environ.get("WORLDPULSE_LLM_API", "openai"), choices=["openai", "anthropic"])
    p.add_argument("--url", default=os.environ.get("WORLDPULSE_LLM_URL"))
    p.add_argument("--model", default=os.environ.get("WORLDPULSE_LLM_MODEL"))
    a = p.parse_args(argv)
    key = os.environ.get("WORLDPULSE_LLM_KEY") or os.environ.get("ANTHROPIC_API_KEY" if a.api == "anthropic" else "OPENAI_API_KEY")
    workspace = Workspace(a.mod)
    if not workspace.mod_dir.is_dir():
        print("no mod folder mods/%s: create it first with python3 tools/modkit.py new %s" % (a.mod, a.mod), file=sys.stderr)
        return 2
    model = (Anthropic if a.api == "anthropic" else OpenAI)(a.url, a.model, key, system_prompt(a.mod))
    if not a.chat:
        emit({"type": "system", "subtype": "init", "model": model.model})
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        text = line
        if not a.chat:
            try:
                msg = json.loads(line)
                text = "".join(b.get("text", "") for b in msg["message"]["content"] if b.get("type") == "text")
            except (ValueError, KeyError, TypeError):
                pass  # a plain line is taken as the message
        try:
            reply, failed = turn(model, workspace, text, a.chat)
            error = None
        except RuntimeError as e:
            reply, failed, error = "", True, str(e)
        if a.chat:
            if error:
                print("error: " + error)
        else:
            emit({"type": "result", "is_error": failed, "result": error or reply})
    return 0


if __name__ == "__main__":
    sys.exit(main())
