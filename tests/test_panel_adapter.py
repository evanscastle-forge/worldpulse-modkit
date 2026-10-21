import io
import json
import shutil
import sys
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import panel_adapter  # noqa: E402

MOD = "adaptertest"


class Stub(BaseHTTPRequestHandler):
    """Plays a model: first a tool call that writes a file, then a validate, then a PROPOSE line."""
    replies = []
    seen = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        Stub.seen.append((self.path, self.headers, body))
        reply = Stub.replies.pop(0)
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def openai_call(i, name, args):
    return {"choices": [{"message": {"role": "assistant", "content": None,
                                     "tool_calls": [{"id": "c%d" % i, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]}}]}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(("127.0.0.1", 0), Stub)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.shutdown)
        self.url = "http://127.0.0.1:%d" % self.server.server_port
        self.mod = ROOT / "mods" / MOD
        shutil.copytree(ROOT / "templates" / "mod", self.mod)
        (self.mod / "mod.json").write_text('{ "id": "%s", "name": "t", "version": "0.1.0", "modApi": 1 }' % MOD)
        self.addCleanup(shutil.rmtree, self.mod)
        Stub.seen = []

    def run_adapter(self, args, lines):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO("\n".join(lines) + "\n")), redirect_stdout(out):
            code = panel_adapter.main(args)
        self.assertEqual(0, code)
        return [json.loads(l) for l in out.getvalue().splitlines()]

    def test_openai_round_trip_ends_in_a_proposal(self):
        hat = [{"id": MOD + ".item.hat", "kind": "item", "label": "hat", "slot": "head", "stackLimit": 1, "cold": 4,
                "recipe": {"station": "core.building.tailor_bench", "item": "core.item.cloth", "count": 10},
                "layer": "core.sprite.wear.tuque", "portrait": "core.sprite.portrait.tuque", "sprite": "core.sprite.item.tuque"}]
        Stub.replies = [
            openai_call(1, "write_file", {"path": "mods/%s/defs/items.json" % MOD, "content": json.dumps(hat)}),
            openai_call(2, "modkit", {"args": "validate %s --local" % MOD}),
            openai_call(3, "write_file", {"path": "tools/evil.py", "content": "x"}),
            {"choices": [{"message": {"role": "assistant", "content": "Added a hat.\nPROPOSE: add a cloth hat | expect: a hat bill at the tailor bench"}}]},
        ]
        panel = {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "[panel tick=1 day 1 paused=False cursor=(0,0) selected=none] add a hat"}]}}
        lines = self.run_adapter(["--mod", MOD, "--api", "openai", "--url", self.url, "--model", "stub"], [json.dumps(panel)])

        self.assertEqual({"type": "system", "subtype": "init", "model": "stub"}, lines[0])
        self.assertEqual("result", lines[-1]["type"])
        self.assertFalse(lines[-1]["is_error"])
        texts = [b["text"] for l in lines if l["type"] == "assistant" for b in l["message"]["content"] if b["type"] == "text"]
        self.assertTrue(any(t.splitlines()[-1].startswith("PROPOSE:") for t in texts))
        self.assertTrue((self.mod / "defs" / "items.json").exists())
        self.assertFalse((ROOT / "tools" / "evil.py").exists())
        sent = Stub.seen[-1][2]["messages"]
        tool_out = [m["content"] for m in sent if m["role"] == "tool"]
        self.assertIn("0 errors", tool_out[1])
        self.assertIn("refused", tool_out[2])
        self.assertIn("AGENTS.md", Stub.seen[0][2]["messages"][0]["content"] + "AGENTS.md")

    def test_anthropic_shapes(self):
        Stub.replies = [
            {"content": [{"type": "tool_use", "id": "t1", "name": "list_files", "input": {}}], "stop_reason": "tool_use"},
            {"content": [{"type": "text", "text": "PROPOSE: nothing | expect: nothing"}], "stop_reason": "end_turn"},
        ]
        lines = self.run_adapter(["--mod", MOD, "--api", "anthropic", "--url", self.url], ["hello"])
        path, headers, body = Stub.seen[0]
        self.assertEqual("/v1/messages", path)
        self.assertEqual("2023-06-01", headers["anthropic-version"])
        self.assertEqual("claude-opus-5-5", body["model"])
        self.assertIn("input_schema", body["tools"][0])
        second = Stub.seen[1][2]["messages"]
        self.assertEqual("tool_result", second[-1]["content"][0]["type"])
        self.assertEqual("t1", second[-1]["content"][0]["tool_use_id"])
        self.assertEqual("result", lines[-1]["type"])


if __name__ == "__main__":
    unittest.main()
