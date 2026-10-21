#!/usr/bin/env python3
"""modkit: the WorldPulse modding toolkit's one script. Python 3.8+, standard library only.

  python3 tools/modkit.py <command> --help

Commands
  new ID               start a mod in mods/ID from templates/mod
  new-def KIND NAME    copy a known-good def into a mod under a new id (--like core.item.tuque)
  override ID          copy a core def whole into a mod, to change it (e.g. core.biome.tundra)
  validate [MOD]       check a mod against the schemas and core content (no game needed)
  test [MOD]           the game's own checks: modtool validate + simulate (needs the game)
  sprite ID|FILE       preview a sprite in the terminal, or --png it
  install MOD          copy a mod into the game's mods folder and reload a running game
  uninstall MOD        remove it again;  restore MOD puts back the copy install replaced
  pack MOD             validate, then zip the mod into dist/
  bundle               rebuild bundle/*.md and the generated parts of docs/ (--check: verify only)
  sync                 copy agents/*.md to .claude/agents/
  doctor               where the game and mods folder are; versions

Every message says what to do next. Exit code 0 = fine, 1 = problems found, 2 = could not run.
"""

import argparse
import difflib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "reference"
SCHEMAS = ROOT / "schemas"
MODS = ROOT / "mods"
EXAMPLES = ROOT / "examples"
TEMPLATE = ROOT / "templates" / "mod"
GAME_JSON = ROOT / "game.json"

ERROR, WARNING, NOTE = "error", "warning", "note"
ID_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
MOD_ID_RE = re.compile(r"^[a-z0-9_]+$")
PALETTE_RE = re.compile(r"^(#[0-9a-fA-F]{6}|\$(skin|hair|main)[+-]?)$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
KIND_FILES = {}  # kind -> default defs file name for new-def


def fail(message, code=2):
    print("error: " + message, file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- JSON with comments

def strip_jsonc(text):
    """The game reads JSON with // and /* */ comments and trailing commas; so do we."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            end = n if j < 0 else j + 2
            out.append("\n" * text.count("\n", i, end))
            i = end
            continue
        elif c in "]}":
            k = len(out) - 1
            while k >= 0 and out[k] in " \t\r\n":
                k -= 1
            if k >= 0 and out[k] == ",":
                out[k] = " "
        out.append(c)
        i += 1
    return "".join(out)


def load_jsonc(path):
    return json.loads(strip_jsonc(Path(path).read_text(encoding="utf-8")))


# ---------------------------------------------------------------- content on disk

def def_files(mod):
    """A mod's def files in the game's load order: all *.json except mod.json and tests/."""
    mod = Path(mod)
    files = []
    for p in sorted(mod.rglob("*.json"), key=lambda p: p.relative_to(mod).as_posix()):
        rel = p.relative_to(mod).as_posix()
        if rel == "mod.json" or rel.startswith("tests/"):
            continue
        files.append(p)
    return files


def read_defs(mod, issues=None):
    """[(relative file, def dict)] of a mod folder. Parse errors go to issues."""
    mod = Path(mod)
    found = []
    for path in def_files(mod):
        rel = path.relative_to(mod).as_posix()
        if path.name != path.name.lower() and issues is not None:
            issues.append(issue(WARNING, "content filenames must be lowercase; rename the file", rel))
        try:
            data = load_jsonc(path)
        except (ValueError, UnicodeDecodeError) as e:
            if issues is not None:
                issues.append(issue(ERROR, "not valid JSON: %s. The whole file is skipped until this is fixed" % e, rel))
            continue
        if path.name == "flags.json":
            if issues is not None:
                if not isinstance(data, dict):
                    issues.append(issue(ERROR, "flags.json must be an object of name: true|false", rel))
                else:
                    for k, v in data.items():
                        if not isinstance(v, bool):
                            issues.append(issue(ERROR, "flag '%s' must be true or false" % k, rel))
            continue
        for n, d in enumerate(data if isinstance(data, list) else [data]):
            if isinstance(d, dict) and isinstance(d.get("id"), str) and "." in d["id"]:
                found.append((rel, d))
            elif issues is not None:
                issues.append(issue(ERROR, 'def #%d needs a string "id" with a namespace, such as "mymod.item.my_thing"; it is skipped' % (n + 1), rel))
    return found


def mod_info(mod):
    path = Path(mod) / "mod.json"
    if not path.exists():
        return None
    try:
        return load_jsonc(path)
    except ValueError:
        return None


def mod_id(mod):
    info = mod_info(mod) or {}
    return info.get("id") if isinstance(info.get("id"), str) else Path(mod).resolve().name


def find_mod(name):
    """A mod given as a path, or as an id under mods/ or examples/."""
    if name is None:
        here = Path.cwd()
        for p in [here] + list(here.parents):
            if (p / "mod.json").exists():
                return p
        mods = sorted(p for p in MODS.iterdir() if p.is_dir()) if MODS.exists() else []
        if len(mods) == 1:
            return mods[0]
        fail("which mod? give its folder or id (mods: %s)" % (", ".join(p.name for p in mods) or "none yet; run: modkit new MYMOD"))
    p = Path(name)
    if p.is_dir():
        return p.resolve()
    for base in (MODS, EXAMPLES):
        for cand in (base / name, base / name.replace("_", "-")):
            if cand.is_dir():
                return cand.resolve()
        if base.exists():
            for cand in base.iterdir():
                if cand.is_dir() and mod_id(cand) == name:
                    return cand.resolve()
    fail("no mod '%s' (looked for a folder, then mods/ and examples/)" % name)


def base_folders(mod):
    """What a mod loads on top of: core, then the mods its mod.json requires."""
    folders = [REFERENCE / "core"]
    if Path(mod).resolve() == (REFERENCE / "core").resolve():
        return []
    for req in (mod_info(mod) or {}).get("requires") or []:
        hit = None
        for base in (Path(mod).resolve().parent, MODS, EXAMPLES):
            if base.exists():
                for cand in [base / req] + [c for c in base.iterdir() if c.is_dir()]:
                    if cand.is_dir() and mod_id(cand) == req:
                        hit = cand
                        break
            if hit:
                break
        if not hit:
            fail("the mod requires '%s'; put that mod beside it or in mods/" % req)
        folders.append(hit)
    return folders


def load_pack(folders):
    """id -> def, later folders overriding earlier ones, like the game."""
    pack = {}
    for folder in folders:
        for _, d in read_defs(folder):
            pack[d["id"]] = d
    return pack


# ---------------------------------------------------------------- schemas

_schemas = None


def schemas():
    global _schemas
    if _schemas is None:
        if not SCHEMAS.exists():
            fail("no schemas/ folder: this checkout is incomplete")
        _schemas = {p.name[: -len(".schema.json")]: json.loads(p.read_text(encoding="utf-8")) for p in SCHEMAS.glob("*.schema.json")}
    return _schemas


def kinds():
    return sorted(k for k, s in schemas().items() if "kind" in s.get("properties", {}) and "const" in s["properties"]["kind"])


def singletons():
    return sorted(k for k, s in schemas().items() if "const" in s.get("properties", {}).get("id", {}))


def schema_for(d):
    did, kind = d.get("id"), d.get("kind")
    s = schemas()
    if did in s and did in singletons():
        return s[did]
    if isinstance(kind, str) and kind in kinds():
        return s[kind]
    return None


def resolve(schema, root):
    while "$ref" in schema:
        schema = root["$defs"][schema["$ref"].split("/")[-1]]
    return schema


def type_name(schema, root):
    schema = resolve(schema, root)
    t = schema.get("type")
    if t == "integer":
        return "a whole number"
    if t == "boolean":
        return "true or false"
    if t == "string":
        return "text"
    if t == "array":
        inner = resolve(schema.get("items", {}), root)
        return "a list of objects" if inner.get("type") == "object" else "a list of " + type_name(inner, root)
    if t == "object" and "properties" in schema:
        return "an object (%s)" % ", ".join(schema["properties"])
    if t == "object":
        return "an object of name: " + type_name(schema.get("additionalProperties", {}), root)
    return "a value"


def describe(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return 'text "%s"' % v
    if isinstance(v, (int, float)):
        return "number %s" % json.dumps(v)
    if isinstance(v, list):
        return "a list [...]"
    if isinstance(v, dict):
        return "an object {...}"
    return "null"


def suggest(wrong, candidates):
    best = difflib.get_close_matches(wrong.lower(), [c.lower() for c in candidates], n=1, cutoff=0.6)
    if not best:
        return ""
    for c in candidates:
        if c.lower() == best[0]:
            return " (did you mean '%s'?)" % c
    return ""


def issue(severity, message, file=None, def_id=None, field=None):
    return {"severity": severity, "message": message, "file": file, "def": def_id, "field": field}


def join(path, name):
    return name if not path else path + "." + name


class Checker:
    def __init__(self, pack, issues):
        self.pack, self.issues = pack, issues

    def add(self, sev, msg, field=None):
        self.issues.append(issue(sev, msg, self.file, self.def_id, field))

    def check_def(self, d, schema, file):
        self.file, self.def_id, self.root = file, d.get("id"), schema
        self.check_object(d, schema, "", top=True)

    def check_object(self, obj, schema, path, top=False):
        schema = resolve(schema, self.root)
        if not isinstance(obj, dict):
            self.add(ERROR, "expected an object {...}, found %s" % describe(obj), path or None)
            return
        props = schema.get("properties", {})
        shown = [k for k in props if not (top and k in ("id", "kind"))]
        for k, v in obj.items():
            at = join(path, k)
            if k.startswith("_") or k == "$schema":
                continue
            if k not in props:
                ci = next((p for p in shown if p.lower() == k.lower()), None)
                if ci:
                    self.add(ERROR, 'field names are case-sensitive: write "%s"' % ci, at)
                else:
                    self.add(ERROR, "unknown field: the game ignores it%s. Fields here: %s. To leave a note, start the name with _"
                             % (suggest(k, shown), ", ".join(shown)), at)
                continue
            if top and k == "id":
                continue
            self.check_value(v, props[k], at, k)
        for r in schema.get("required", []):
            if r not in obj and not (top and r == "id"):
                self.add(ERROR, 'missing required field "%s" (%s)' % (r, type_name(props.get(r, {}), self.root)), join(path, r))

    def check_value(self, v, schema, path, name, in_list=False):
        nullable = schema.get("x-nullable", False) and not in_list
        s = resolve(schema, self.root)
        if v is None:
            if not nullable:
                self.add(ERROR, "cannot be null; expected %s" % type_name(s, self.root), path)
            return
        if "const" in s:
            if v != s["const"]:
                self.add(ERROR, 'must be "%s" here' % s["const"], path)
            return
        t = s.get("type")
        bad = lambda: self.add(ERROR, "expected %s, found %s" % (type_name(s, self.root), describe(v)), path)
        if t == "integer":
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                bad()
            elif isinstance(v, float) or not (-2**31 <= v < 2**31):
                self.add(ERROR, "must be a whole number (the game uses integers only: percent, per-mille, ticks), found %s" % json.dumps(v), path)
        elif t == "boolean":
            if not isinstance(v, bool):
                bad()
        elif t == "string":
            if not isinstance(v, str):
                bad()
                return
            if "enum" in s and v not in s["enum"]:
                self.add(ERROR, "must be one of: %s%s" % (", ".join(s["enum"]), suggest(v, s["enum"])), path)
            if "x-known" in s and v not in s["x-known"]:
                self.add(WARNING, "'%s' has no behaviour in the game; known values: %s" % (v, ", ".join(s["x-known"])), path)
            if name == "color" and not HEX_RE.match(v):
                self.add(WARNING, 'colors are "#rrggbb", e.g. "#7a3f52"', path)
            if "x-ref" in schema:
                self.check_ref(v, schema["x-ref"], schema.get("x-size"), path)
        elif t == "array":
            if not isinstance(v, list):
                bad()
                return
            item = s.get("items", {})
            for i, x in enumerate(v):
                at = "%s[%d]" % (path, i)
                if resolve(item, self.root).get("type") == "object" and "properties" in resolve(item, self.root):
                    self.check_object(x, item, at)
                    if "x-ref" in schema and isinstance(x, dict) and isinstance(x.get("id"), str):
                        self.check_ref(x["id"], schema["x-ref"], schema.get("x-size"), at + ".id")
                else:
                    sub = dict(item)
                    if "x-ref" in schema:
                        sub["x-ref"] = schema["x-ref"]
                    self.check_value(x, sub, at, name, in_list=True)
        elif t == "object":
            if not isinstance(v, dict):
                bad()
                return
            if "properties" in s:
                self.check_object(v, s, path)
            else:
                for k, x in v.items():
                    self.check_value(x, s.get("additionalProperties", {}), join(path, k), k, in_list=True)

    def check_ref(self, ref, kind, size, path):
        target = self.pack.get(ref)
        if target is None:
            cands = [i for i, d in self.pack.items() if d.get("kind") == kind]
            self.add(ERROR, "no %s '%s'%s. Define it in the mod, or use an existing %s id" % (kind, ref, suggest(ref, cands), kind), path)
        elif target.get("kind") != kind:
            self.add(ERROR, "'%s' is a %s, but this field needs a %s" % (ref, target.get("kind") or "def without a kind", kind), path)
        elif kind == "sprite" and size and target.get("size", 16) != size:
            self.add(ERROR, "sprite '%s' is %spx; this field needs a %dpx sprite" % (ref, target.get("size", 16), size), path)


def collect_refs(obj, schema, root, into):
    schema = resolve(schema, root)
    if not isinstance(obj, dict):
        return
    for k, fs in schema.get("properties", {}).items():
        if k not in obj:
            if "x-ref" in fs and isinstance(fs.get("default"), str):
                into.add(fs["default"])
            continue
        v = obj[k]
        if isinstance(v, str) and "x-ref" in fs:
            into.add(v)
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, str) and "x-ref" in fs:
                    into.add(x)
                elif isinstance(x, dict):
                    if "x-ref" in fs and isinstance(x.get("id"), str):
                        into.add(x["id"])
                    collect_refs(x, fs.get("items", {}), root, into)
        elif isinstance(v, dict) and "$ref" in fs:
            collect_refs(v, fs, root, into)


def validate(mod):
    """The layer-1 check. Mirrors the game's `modtool validate` without needing the game."""
    mod = Path(mod)
    issues = []
    folder = mod.resolve().name
    mid = folder
    info_path = mod / "mod.json"
    if not info_path.exists():
        if folder != "core":
            issues.append(issue(WARNING, 'no mod.json: add one with at least {"id": "%s", "name": "...", "version": "0.1.0", "modApi": %d}'
                                % (folder, game_info().get("modApi", 1)), "mod.json"))
    else:
        try:
            info = load_jsonc(info_path)
            ch = Checker({}, issues)
            ch.file, ch.def_id, ch.root = "mod.json", None, schemas()["mod"]
            ch.check_object(info, schemas()["mod"], "")
            mid = info.get("id") if isinstance(info.get("id"), str) else folder
            if not MOD_ID_RE.match(mid):
                issues.append(issue(ERROR, 'the mod id is one lowercase word (letters, digits, underscores), e.g. "furhats"; it prefixes every id in the mod', "mod.json", None, "id"))
            if mid != folder:
                issues.append(issue(WARNING, "the folder is '%s' but the mod id is '%s'; name the folder after the id" % (folder, mid), "mod.json", None, "id"))
            api = info.get("modApi")
            if isinstance(api, int) and api > game_info().get("modApi", 1):
                issues.append(issue(ERROR, "made for mod API %d, but the toolkit's game has %d: update the game and the toolkit" % (api, game_info().get("modApi", 1)), "mod.json", None, "modApi"))
        except ValueError as e:
            issues.append(issue(ERROR, "not valid JSON: %s" % e, "mod.json"))

    bases = base_folders(mod)
    base = load_pack(bases)
    mine = read_defs(mod, issues)
    for rel in [p.relative_to(mod).as_posix() for p in def_files(mod)]:
        if rel == "expect.json":
            issues.append(issue(WARNING, "expect.json in the mod root is loaded as a def file; move it to tests/expect.json", rel))
    pack = dict(base)
    for _, d in mine:
        pack[d["id"]] = d

    seen, overrides = {}, []
    checker = Checker(pack, issues)
    for file, d in mine:
        did, kind = d["id"], d.get("kind")
        if did in seen:
            issues.append(issue(ERROR, "id defined twice (first in %s); the later one silently replaces the earlier. Rename one" % seen[did], file, did))
        seen[did] = file
        if not ID_RE.match(did):
            issues.append(issue(WARNING, 'ids are lowercase words joined by dots and underscores, e.g. "%s.item.fur_hat"' % mid, file, did))
        if did in base:
            overrides.append(did)
            issues.append(issue(NOTE, "overrides a def the mod loads on top of: the whole def is replaced, so copy every field you want to keep (other mods that override it will conflict)", file, did))
        elif not did.startswith(mid + "."):
            issues.append(issue(WARNING, 'new ids should start with the mod id: "%s.%s"' % (mid, did.split(".", 1)[1]), file, did))
        schema = schema_for(d)
        if schema is None:
            if kind is None:
                issues.append(issue(ERROR, 'no "kind": the game never uses this def. Add one of: %s' % ", ".join(kinds()), file, did))
            else:
                issues.append(issue(ERROR, "unknown kind '%s'%s; kinds are: %s" % (kind, suggest(str(kind), kinds()), ", ".join(kinds())), file, did, "kind"))
            continue
        checker.check_def(d, schema, file)
        if not any(i["def"] == did and i["severity"] == ERROR and i["file"] == file for i in issues):
            check_rules(d, pack, file, issues)

    referenced = set()
    for d in pack.values():
        s = schema_for(d)
        if s:
            collect_refs(d, s, s, referenced)
    for file, d in mine:
        did, kind = d["id"], d.get("kind")
        if did in base or any(i["def"] == did and i["severity"] == ERROR for i in issues):
            continue
        if kind == "sprite" and did not in referenced:
            issues.append(issue(NOTE, "no def uses this sprite (set an item's sprite/layer/portrait, a plant's, building's or animal's sprite to its id)", file, did))
        elif kind == "plant" and did not in referenced and not d.get("sowable", False):
            issues.append(issue(WARNING, 'will never appear: no biome lists it in "plants" and it is not sowable. Override a biome to add it, or set "sowable": true', file, did))
        elif kind == "animal" and did not in referenced:
            issues.append(issue(WARNING, 'will never appear: no biome lists it in "animals". Override a biome (copy it whole) and add {"id": "%s", "weight": 10}' % did, file, did))
        elif kind == "thought" and not did.startswith("core.thought."):
            issues.append(issue(WARNING, "the game only triggers its built-in thoughts; a new thought id is never felt (see docs/limits.md). Override a core.thought.* id to change one", file, did))
        elif kind == "item" and did not in referenced and d.get("recipe") is None:
            issues.append(issue(WARNING, "nothing makes or drops this item: give it a recipe, or reference it from a plant's harvestItem, a building's product or mineItem, an animal's meatItem/leatherItem, or worldgen startingItems", file, did))
        elif kind == "building" and not d.get("natural", False) and d.get("costItem") is None:
            issues.append(issue(WARNING, "not in the build menu: a building needs a costItem (and costCount) to be built", file, did))
        elif kind == "biome" and d.get("priority", 0) <= 0:
            issues.append(issue(NOTE, "a new biome only claims tiles where its temperature and rain ranges fit and its priority beats the others; it affects new worlds only", file, did))
    return {"mod": str(mod), "modId": mid, "defs": len(mine), "overrides": overrides, "issues": issues}


def check_rules(d, pack, file, issues):
    """Rules that span fields, as the game checks them."""
    did, kind = d["id"], d.get("kind")
    add = lambda sev, msg, field=None: issues.append(issue(sev, msg, file, did, field))
    if kind == "sprite":
        size = d.get("size", 16)
        if size not in (8, 16, 32):
            add(ERROR, "size is 8 (icons), 16 (map things, worn layers) or 32 (portraits)", "size")
        palette, rows = d.get("palette"), d.get("rows")
        if palette is None or rows is None:
            add(ERROR, 'a sprite needs "palette" and "rows"')
            return
        for k, v in palette.items():
            if len(k) != 1 or k == ".":
                add(ERROR, "palette keys are single characters other than '.' (which is transparent)", "palette." + k)
            if not PALETTE_RE.match(v):
                add(ERROR, 'palette values are "#rrggbb" or a tint: $main, $skin, $hair, optionally followed by - (darker) or + (lighter)', "palette." + k)
        for name, grid in [("rows", rows)] + [("frames[%d]" % n, f) for n, f in enumerate(d.get("frames") or [])]:
            if len(grid) != size:
                add(ERROR, "has %d rows; a %dpx sprite needs exactly %d" % (len(grid), size, size), name)
            for y, row in enumerate(grid):
                if len(row) != size:
                    add(ERROR, "row %d is %d characters; every row must be exactly %d" % (y, len(row), size), "%s[%d]" % (name, y))
                missing = sorted({c for c in row if c != "." and c not in palette})
                if missing:
                    add(ERROR, 'row %d uses %s not in the palette; add them to "palette" or use \'.\' for transparent'
                        % (y, " ".join("'%s'" % c for c in missing)), "%s[%d]" % (name, y))
    elif kind == "item":
        if d.get("slot"):
            if not d.get("layer"):
                add(ERROR, 'apparel needs "layer": a 16px sprite drawn over the colonist on the map', "layer")
            if not d.get("portrait") and d.get("slot") != "legs":
                add(WARNING, 'apparel shows on the ID card through "portrait", a 32px sprite (legs are below the frame and need none)', "portrait")
            if d.get("stackLimit", 75) > 1:
                add(WARNING, 'apparel is worn one at a time; set "stackLimit": 1', "stackLimit")
            if d.get("armor", 0) > 60:
                add(NOTE, "armor is capped at 60% when worn", "armor")
        r = d.get("recipe")
        if isinstance(r, dict) and r.get("station") in pack and pack[r["station"]].get("use") != "craft":
            add(WARNING, 'colonists only craft at buildings with "use": "craft"; \'%s\' is not one' % r["station"], "recipe.station")
    elif kind == "plant":
        if d.get("harvestYield", 0) > 0 and not d.get("harvestItem"):
            add(WARNING, "harvestYield without harvestItem: harvesting gives nothing", "harvestItem")
        if d.get("tree") and d.get("woodYield", 0) <= 0:
            add(WARNING, "a tree with woodYield 0 gives no wood when chopped", "woodYield")
        if d.get("minTemp", 1) >= d.get("maxTemp", 45):
            add(ERROR, "minTemp must be below maxTemp, or it never grows", "minTemp")
    elif kind == "animal":
        if not d.get("sprite"):
            add(WARNING, 'no sprite: set one (core.sprite.animal.small, .deer, .boar, .canine, .feline, .bear are tinted by "color")', "sprite")
        if d.get("minTemp", -100) >= d.get("maxTemp", 100):
            add(ERROR, "minTemp must be below maxTemp, or it never arrives", "minTemp")
    elif did == "core.rpg":
        keys = sorted(a.get("key") for a in d.get("attributes") or [])
        if keys != ["cha", "con", "dex", "int", "str", "wis"]:
            add(ERROR, "attributes must be exactly str, dex, con, int, wis, cha (the game reads them by key); change labels, colors and icons, not keys", "attributes")
        if sorted((d.get("skills") or {}).keys()) != sorted(game_info().get("workTypes", [])):
            add(ERROR, "skills must have exactly the work types: %s" % ", ".join(game_info().get("workTypes", [])), "skills")


def format_report(r):
    order = {ERROR: 0, WARNING: 1, NOTE: 2}
    lines = []
    for i in sorted(r["issues"], key=lambda i: (order[i["severity"]], i["file"] or "", i["def"] or "")):
        where = " ".join(x for x in (i["file"], i["def"], i["field"]) if x)
        lines.append("%s %s: %s" % (i["severity"].upper(), where, i["message"]))
    errors = sum(1 for i in r["issues"] if i["severity"] == ERROR)
    warnings = sum(1 for i in r["issues"] if i["severity"] == WARNING)
    notes = sum(1 for i in r["issues"] if i["severity"] == NOTE)
    lines.append("%s: %d defs, %d errors, %d warnings, %d notes%s%s" % (
        r["modId"], r["defs"], errors, warnings, notes,
        (", overrides " + " ".join(r["overrides"])) if r["overrides"] else "",
        " - OK" if errors == 0 else " - FIX THE ERRORS"))
    return "\n".join(lines)


# ---------------------------------------------------------------- the game

def game_info():
    try:
        return json.loads(GAME_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def local_config():
    path = ROOT / "modkit.local.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except ValueError:
        return {}


def find_game():
    """The command that runs the game's tools, or None. WORLDPULSE_GAME (or "game" in
    modkit.local.json) is the game's Headless.dll / headless executable, or the folder holding it."""
    candidates = [os.environ.get("WORLDPULSE_GAME"), local_config().get("game")]
    home = Path.home()
    candidates += [str(p) for p in (
        home / ".local/share/Steam/steamapps/common/WorldPulse",
        Path("C:/Program Files (x86)/Steam/steamapps/common/WorldPulse"),
        home / "Library/Application Support/Steam/steamapps/common/WorldPulse",
    )]
    for c in candidates:
        if not c:
            continue
        p = Path(c).expanduser()
        if p.is_dir():
            for name in ("Headless.dll", "Headless.exe", "Headless", "worldpulse-headless"):
                if (p / name).exists():
                    p = p / name
                    break
        if p.is_file():
            if p.suffix == ".dll":
                dotnet = shutil.which("dotnet") or str(home / ".dotnet" / "dotnet")
                return [dotnet, str(p)]
            return [str(p)]
    return None


def run_game(args, capture=False):
    game = find_game()
    if game is None:
        return None
    return subprocess.run(game + args, capture_output=capture, text=True)


def data_dir():
    if os.environ.get("WORLDPULSE_DATA"):
        return Path(os.environ["WORLDPULSE_DATA"]).resolve()
    home = Path.home()
    if sys.platform.startswith("win"):
        return Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")) / "WorldPulse"
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "WorldPulse"
    xdg = os.environ.get("XDG_DATA_HOME")
    return Path(xdg if xdg else home / ".local" / "share") / "worldpulse"


def mods_dir():
    return data_dir() / "mods"


# ---------------------------------------------------------------- sprites

def tint(value, tints):
    if value.startswith("#"):
        return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)
    base = tints.get(value[1:].rstrip("+-"), tints["main"])
    r, g, b = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
    if value.endswith("-"):
        return tuple(int(c * 0.72) for c in (r, g, b))
    if value.endswith("+"):
        return tuple(int(c + (255 - c) * 0.3) for c in (r, g, b))
    return r, g, b


def sprite_pixels(d, tints, frame=0):
    rows = d["rows"] if frame == 0 else d["frames"][frame - 1]
    pal = {k: tint(v, tints) for k, v in d["palette"].items() if PALETTE_RE.match(v)}
    return [[pal.get(c) if c != "." else None for c in row] for row in rows]


def write_png(path, pixels, scale):
    h, w = len(pixels) * scale, max(len(r) for r in pixels) * scale
    raw = bytearray()
    for row in pixels:
        line = bytearray([0])
        for px in row:
            rgba = (0, 0, 0, 0) if px is None else (px[0], px[1], px[2], 255)
            line += bytes(rgba) * scale
        line += bytes(4 * (w - len(row) * scale))
        raw += line * scale
    chunk = lambda tag, data: struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def print_sprite(pixels, color):
    for row in pixels:
        line = ""
        for px in row:
            if px is None:
                line += "\x1b[0m. " if color else ". "
            elif color:
                line += "\x1b[48;2;%d;%d;%dm  " % px
            else:
                line += "##"
        print(line + ("\x1b[0m" if color else ""))


# ---------------------------------------------------------------- commands

def cmd_new(a):
    mid = a.id
    if not MOD_ID_RE.match(mid):
        fail("a mod id is one lowercase word: letters, digits, underscores (e.g. furhats)")
    dest = MODS / mid
    if dest.exists():
        fail("%s already exists" % dest)
    shutil.copytree(TEMPLATE, dest)
    for p in dest.rglob("*"):
        if p.is_file() and p.suffix in (".json", ".md"):
            text = p.read_text(encoding="utf-8").replace("{{id}}", mid).replace("{{name}}", a.name or mid)
            text = text.replace("{{modApi}}", str(game_info().get("modApi", 1)))
            p.write_text(text, encoding="utf-8")
    print("created %s\nnext: describe the mod in %s, then add defs (modkit new-def --help)" % (dest.relative_to(ROOT), (dest / "NOTES.md").relative_to(ROOT)))
    return 0


def cmd_new_def(a):
    mod = find_mod(a.mod)
    mid = mod_id(mod)
    pack = load_pack(base_folders(mod) + [mod])
    if a.like not in pack:
        same = [i for i, d in pack.items() if d.get("kind") == a.kind]
        fail("no def '%s'%s. Defs of kind %s: %s" % (a.like, suggest(a.like, list(pack)), a.kind, ", ".join(same[:40])))
    src = json.loads(json.dumps(pack[a.like]))
    kind = src.get("kind") or a.kind
    if kind != a.kind:
        fail("'%s' is a %s, not a %s" % (a.like, kind, a.kind))
    if not re.match(r"^[a-z0-9_]+$", a.name):
        fail("NAME is lowercase letters, digits and underscores, e.g. fur_hat")
    new_id = "%s.%s.%s" % (mid, kind, a.name)
    if new_id in pack:
        fail("%s already exists" % new_id)
    src["id"] = new_id
    if "label" in src:
        src["label"] = a.name.replace("_", " ")
    defs_dir = mod / "defs"
    defs_dir.mkdir(exist_ok=True)
    target = defs_dir / ("%ss.json" % kind if kind != "sprite" else "sprites.json")
    existing = load_jsonc(target) if target.exists() else []
    if not isinstance(existing, list):
        existing = [existing]
    existing.append(src)
    target.write_text(dump_defs(existing), encoding="utf-8")
    print("added %s to %s (a copy of %s). Edit its fields, then run: modkit validate %s" % (new_id, target.relative_to(mod.parent), a.like, mid))
    return 0


def cmd_override(a):
    mod = find_mod(a.mod)
    pack = load_pack(base_folders(mod))
    if a.id not in pack:
        fail("no def '%s' to override%s" % (a.id, suggest(a.id, list(pack))))
    target = mod / "defs" / "overrides.json"
    target.parent.mkdir(exist_ok=True)
    existing = load_jsonc(target) if target.exists() else []
    if any(d.get("id") == a.id for d in existing):
        fail("%s is already in %s" % (a.id, target.relative_to(mod.parent)))
    existing.append(json.loads(json.dumps(pack[a.id])))
    target.write_text(dump_defs(existing), encoding="utf-8")
    print("copied %s whole into %s. Change only what the mod needs and keep the rest; list it under Overrides in NOTES.md"
          % (a.id, target.relative_to(mod.parent)))
    return 0


def dump_defs(defs):
    """One def per block, fields on one line each when short: easy to read and to diff."""
    parts = []
    for d in defs:
        lines = []
        for k, v in d.items():
            lines.append("    %s: %s" % (json.dumps(k), json.dumps(v, ensure_ascii=False)))
        parts.append("  {\n" + ",\n".join(lines) + "\n  }")
    return "[\n" + ",\n".join(parts) + "\n]\n"


def cmd_validate(a):
    mod = find_mod(a.mod)
    r = validate(mod)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(format_report(r))
    ok = not any(i["severity"] == ERROR for i in r["issues"])
    if not a.local and not a.json:
        game = run_game(["modtool", "validate", str(mod)], capture=True)
        if game is None:
            print("(game not found: only the toolkit's checks ran. `modkit doctor` explains how to point at the game)")
        else:
            print("\ngame check:\n" + (game.stdout + game.stderr).strip())
            ok = ok and game.returncode == 0
    return 0 if ok else 1


def cmd_test(a):
    mod = find_mod(a.mod)
    if find_game() is None:
        print("The game was not found, so only `modkit validate` can run. Set WORLDPULSE_GAME to the game's\n"
              "Headless.dll (or folder), or add {\"game\": \"...\"} to modkit.local.json. See docs/testing.md.")
        return 2
    args = ["modtool", "simulate", str(mod)]
    for opt in ("days", "seeds", "biome"):
        if getattr(a, opt):
            args += ["--" + opt, str(getattr(a, opt))]
    v = run_game(["modtool", "validate", str(mod)])
    if v.returncode != 0:
        print("validation failed; fix the errors above before simulating")
        return 1
    print()
    return run_game(args).returncode


def cmd_sprite(a):
    target = a.sprite
    if Path(target).is_file():
        data = load_jsonc(target)
        defs = data if isinstance(data, list) else [data]
        defs = [d for d in defs if d.get("kind") == "sprite"]
        if a.id:
            defs = [d for d in defs if d["id"] == a.id]
    else:
        mod = find_mod(a.mod) if a.mod else None
        pack = load_pack(([mod] if mod else []) + [REFERENCE / "core"] + ([mod] if mod else []))
        defs = [pack[target]] if target in pack else []
        if not defs:
            fail("no sprite '%s'%s" % (target, suggest(target, [i for i, d in pack.items() if d.get("kind") == "sprite"])))
    if not defs:
        fail("no sprite defs found")
    tints = {"main": a.main, "skin": a.skin, "hair": a.hair}
    color = sys.stdout.isatty() and not a.plain
    under = None
    if a.over:
        pack = load_pack([REFERENCE / "core"] + ([find_mod(a.mod)] if a.mod else []))
        if a.over not in pack:
            fail("no sprite '%s' to draw under it" % a.over)
        under = sprite_pixels(pack[a.over], tints)
    for n, d in enumerate(defs):
        frames = [0] + list(range(1, len(d.get("frames") or []) + 1))
        for f in frames:
            px = sprite_pixels(d, tints, f)
            if under is not None:
                px = [[px[y][x] if y < len(px) and x < len(px[y]) and px[y][x] is not None else under[y][x]
                       for x in range(len(under[y]))] for y in range(len(under))]
            if a.png:
                out = Path(a.png)
                if len(defs) > 1 or len(frames) > 1:
                    out = out.with_name("%s-%s%s%s" % (out.stem, d["id"].split(".")[-1], "-%d" % f if f else "", out.suffix))
                write_png(out, px, a.scale)
                print("wrote %s (%dx%d at x%d)" % (out, len(px[0]), len(px), a.scale))
            else:
                print("%s%s (%dpx):" % (d["id"], " frame %d" % f if f else "", d.get("size", 16)))
                print_sprite(px, color)
    return 0


def backup_dir(mid):
    return data_dir() / "modkit-backup" / mid


def reload_game():
    r = run_game(["ctl", "reload"], capture=True)
    if r is None:
        print("game tools not found: the change applies the next time the game starts")
    elif r.returncode != 0:
        print("the game is not running: the change applies the next time it starts")
    else:
        print("reloaded the running game: " + r.stdout.strip())


def cmd_install(a):
    mod = find_mod(a.mod)
    r = validate(mod)
    if any(i["severity"] == ERROR for i in r["issues"]):
        print(format_report(r))
        print("not installed: fix the errors first")
        return 1
    mid = r["modId"]
    dest = mods_dir() / mid
    if dest.exists():
        if backup_dir(mid).exists():
            shutil.rmtree(backup_dir(mid))
        backup_dir(mid).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dest), str(backup_dir(mid)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(mod, dest, ignore=shutil.ignore_patterns("tests", "NOTES.md", "*.zip"))
    print("installed %s into %s" % (mid, dest))
    reload_game()
    return 0


def cmd_uninstall(a):
    mid = a.mod if MOD_ID_RE.match(a.mod) else mod_id(find_mod(a.mod))
    dest = mods_dir() / mid
    if not dest.exists():
        print("%s is not installed in %s" % (mid, mods_dir()))
        return 1
    shutil.rmtree(dest)
    print("removed %s" % dest)
    reload_game()
    return 0


def cmd_restore(a):
    mid = a.mod if MOD_ID_RE.match(a.mod) else mod_id(find_mod(a.mod))
    dest, saved = mods_dir() / mid, backup_dir(mid)
    if dest.exists():
        shutil.rmtree(dest)
    if saved.exists():
        shutil.move(str(saved), str(dest))
        print("restored the previous %s" % mid)
    else:
        print("no previous copy of %s: removed it" % mid)
    reload_game()
    return 0


def cmd_pack(a):
    mod = find_mod(a.mod)
    r = validate(mod)
    if any(i["severity"] == ERROR for i in r["issues"]):
        print(format_report(r))
        print("not packed: fix the errors first")
        return 1
    info = mod_info(mod) or {}
    out = ROOT / "dist" / ("%s-%s.zip" % (r["modId"], info.get("version", "0.0.0")))
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(mod.rglob("*")):
            rel = p.relative_to(mod).as_posix()
            if p.is_file() and not rel.endswith(".zip"):
                z.write(p, "%s/%s" % (r["modId"], rel))
    print("wrote %s" % out.relative_to(ROOT))
    return 0


def cmd_doctor(a):
    gi = game_info()
    print("toolkit      %s" % ROOT)
    print("python       %s" % sys.version.split()[0])
    print("pinned game  modApi %s, save %s, core %s" % (gi.get("modApi"), gi.get("saveVersion"), gi.get("coreHash")))
    game = find_game()
    print("game tools   %s" % (" ".join(game) if game else "not found (set WORLDPULSE_GAME to the game's Headless.dll or folder)"))
    if game:
        r = run_game(["modtool", "version", "--json"], capture=True)
        try:
            v = json.loads(r.stdout)
            match = v.get("modApi") == gi.get("modApi")
            print("game         modApi %s, save %s, core %s%s" % (v.get("modApi"), v.get("saveVersion"), v.get("coreHash"),
                  "" if match else "  <- differs from the toolkit: update one of them"))
            if v.get("coreHash") != gi.get("coreHash"):
                print("             the game's core content differs from reference/core: update the toolkit (git pull)")
        except ValueError:
            print("game         could not run `modtool version`: %s" % (r.stderr.strip() or r.stdout.strip())[:200])
    print("mods folder  %s" % mods_dir())
    return 0


def cmd_sync(a):
    src, dst = ROOT / "agents", ROOT / ".claude" / "agents"
    dst.mkdir(parents=True, exist_ok=True)
    for old in dst.glob("*.md"):
        old.unlink()
    for p in sorted(src.glob("*.md")):
        if p.name == "README.md":
            continue
        text = p.read_text(encoding="utf-8")
        (dst / p.name).write_text(text.replace("\n---\n", "\n---\n<!-- generated from agents/%s by `modkit sync`; edit that file -->\n" % p.name, 1), encoding="utf-8")
    print("synced %d role cards to .claude/agents/" % len(list(dst.glob("*.md"))))
    return 0


# ---------------------------------------------------------------- docs and bundle

DOC_PAGES = {  # schema -> api page
    "terrain": "terrain", "biome": "biome", "plant": "plant", "item": "item", "building": "building", "weather": "weather",
    "animal": "animal", "roof": "roof-and-rooms", "core.rooms": "roof-and-rooms", "thought": "thought", "sprite": "sprite",
    "core.colonist": "singletons", "core.names": "singletons", "core.worldgen": "singletons", "core.rpg": "singletons",
    "core.looks": "singletons", "mod": "mod-json",
}
FIELDS_RE = re.compile(r"<!-- fields:(\S+) -->\n(.*?)<!-- /fields -->", re.S)
ROW_RE = re.compile(r"^\| `([^`]+)` \|[^|]*\|[^|]*\|(.*)\|\s*$")
GEN_RE = re.compile(r"<!-- generated:(\S+) -->\n(.*?)<!-- /generated -->", re.S)


def field_rows(schema_name):
    """[(field path, type, default)] for a schema, nested records flattened as parent.field."""
    s = schemas()[schema_name]
    out = []

    def walk(obj, prefix):
        required = set(obj.get("required", []))
        props = obj["properties"]
        keys = sorted(props, key=lambda k: (prefix != "" or k not in ("id", "kind"), list(props).index(k)))
        for k in keys:
            f = props[k]
            if prefix == "" and k == "id" and "const" not in f and schema_name != "mod":
                continue
            r = resolve(f, s)
            t = type_name(f, s)
            items = resolve(r.get("items", {}), s) if r.get("type") == "array" else None
            if "enum" in r:
                t = "one of " + ", ".join(r["enum"])
            if "x-ref" in f:
                size = " (%dpx)" % f["x-size"] if "x-size" in f else ""
                if r.get("type") == "string":
                    t = "%s id%s" % (f["x-ref"], size)
                elif items is not None and items.get("type") == "string":
                    t = "list of %s ids" % f["x-ref"]
                else:
                    t = "list of objects; each id is a %s id" % f["x-ref"]
            if "const" in f:
                t = '"%s"' % f["const"]
            dflt = "required" if k in required and not (prefix == "" and k in ("id", "kind")) else ("" if f.get("default") is None else json.dumps(f["default"]))
            out.append((prefix + k, t, dflt))
            if items is not None and "properties" in items:
                walk(items, prefix + k + "[].")
            elif "properties" in r and r is not s:
                walk(r, prefix + k + ".")

    walk(s, "")
    return out


def render_fields(names, old_text):
    meanings = {}
    for line in old_text.splitlines():
        m = ROW_RE.match(line)
        if m:
            meanings[m.group(1)] = m.group(2).strip()
    lines = ["| field | type | default | meaning |", "| --- | --- | --- | --- |"]
    missing = []
    for name in names.split(","):
        for k, t, d in field_rows(name):
            meaning = meanings.get(k, "TODO")
            if k in ("kind", "id") and t.startswith('"'):
                meaning = "always this value"
            elif k == "kind":
                meaning = "optional; the game finds this def by its id"
            if meaning in ("", "TODO"):
                missing.append(k)
            lines.append("| `%s` | %s | %s | %s |" % (k, t, d, meaning or "TODO"))
    return "\n".join(lines) + "\n", missing


def balance_table():
    core = load_pack([REFERENCE / "core"])
    spec = [
        ("plant", ["growTicks", "harvestYield", "woodYield", "nutrition", "minTemp", "maxTemp", "workTicks"]),
        ("item", ["nutrition", "stackLimit", "cold", "heat", "armor"]),
        ("building", ["costCount", "workTicks", "heat"]),
        ("animal", ["maxHealth", "damage", "attackTicks", "moveTicks", "meatYield", "leatherYield", "size"]),
        ("thought", ["mood", "ticks"]),
        ("weather", ["weight", "tempOffset", "growth"]),
    ]
    out = []
    for kind, fields in spec:
        defs = [d for d in core.values() if d.get("kind") == kind]
        props = schemas()[kind]["properties"]
        out.append("**%s** (%d in core)\n\n| field | min | typical | max | default |\n| --- | --- | --- | --- | --- |" % (kind, len(defs)))
        for f in fields:
            vals = sorted(d.get(f, props[f].get("default", 0)) for d in defs if f in d)
            if not vals:
                continue
            out.append("| `%s` | %s | %s | %s | %s |" % (f, vals[0], vals[len(vals) // 2], vals[-1], props[f].get("default", "")))
        out.append("")
    return "\n".join(out)


def example(def_id):
    """A core def as a json block, one field per line."""
    d = load_pack([REFERENCE / "core"]).get(def_id)
    if d is None:
        return "(no %s in this game version)\n" % def_id
    return "```json\n" + dump_defs([d])[2:-3].replace("\n  ", "\n").strip() + "\n```\n"


def ids_table():
    core = load_pack([REFERENCE / "core"])
    out = []
    for kind in kinds():
        ids = sorted(i for i, d in core.items() if d.get("kind") == kind)
        out.append("- **%s**: %s" % (kind, ", ".join("`%s`" % i for i in ids)))
    out.append("- **singletons**: %s" % ", ".join("`%s`" % i for i in singletons()))
    return "\n".join(out) + "\n"


def regenerate_docs(check):
    stale, todo = [], []
    for page in sorted((ROOT / "docs").rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        new = text

        def fields(m):
            body, missing = render_fields(m.group(1), m.group(2))
            todo.extend("%s: %s" % (page.relative_to(ROOT), k) for k in missing)
            return "<!-- fields:%s -->\n%s<!-- /fields -->" % (m.group(1), body)

        def generated(m):
            name = m.group(1)
            body = example(name.split(":", 1)[1]) if name.startswith("example:") else {"balance": balance_table, "ids": ids_table}[name]()
            return "<!-- generated:%s -->\n%s<!-- /generated -->" % (m.group(1), body)

        new = FIELDS_RE.sub(fields, new)
        new = GEN_RE.sub(generated, new)
        if new != text:
            stale.append(str(page.relative_to(ROOT)))
            if not check:
                page.write_text(new, encoding="utf-8")
    covered = set()
    for page in (ROOT / "docs" / "api").glob("*.md"):
        for m in FIELDS_RE.finditer(page.read_text(encoding="utf-8")):
            covered.update(m.group(1).split(","))
    uncovered = sorted(set(schemas()) - covered)
    return stale, todo, uncovered


SMALL = ["AGENTS.md", "docs/concepts.md", "docs/limits.md", "docs/api/item.md", "docs/api/plant.md", "docs/api/building.md",
         "docs/api/animal.md", "docs/api/biome.md", "docs/api/sprite.md", "docs/api/mod-json.md"]
FULL = ["README.md", "AGENTS.md", "docs/concepts.md", "docs/limits.md", "docs/compatibility.md", "docs/balance.md", "docs/art.md",
        "docs/testing.md", "docs/api/*.md", "workflows/*.md", "agents/*.md", "docs/ids.md"]
BUDGET = {"modding-small.md": 9000, "modding-full.md": 40000}  # tokens, at ~4 characters each


def bundle_text(patterns, title, intro):
    parts = ["# %s\n\n%s\n" % (title, intro)]
    seen = set()
    for pat in patterns:
        for p in sorted(ROOT.glob(pat)):
            rel = p.relative_to(ROOT).as_posix()
            if rel in seen or p.name == "README.md" and rel != "README.md":
                continue
            seen.add(rel)
            body = re.sub(r"<!-- [^>]* -->\n?", "", p.read_text(encoding="utf-8"))
            parts.append("\n---\n<!-- file: %s -->\n\n%s" % (rel, body.strip() + "\n"))
    return "".join(parts)


def cmd_bundle(a):
    stale, todo, uncovered = regenerate_docs(a.check)
    gi = game_info()
    intro = ("Everything an AI assistant needs to write WorldPulse mods, in one file. Game: mod API %s, core content %s.\n"
             "Paste or attach this file, then describe the mod you want. Follow the rules in AGENTS.md exactly." % (gi.get("modApi"), gi.get("coreHash")))
    bundles = {
        "modding-small.md": bundle_text(SMALL, "WorldPulse modding (small)", intro + "\nThis is the short version for small models; modding-full.md has everything."),
        "modding-full.md": bundle_text(FULL, "WorldPulse modding (full)", intro),
    }
    problems = []
    out = ROOT / "bundle"
    out.mkdir(exist_ok=True)
    for name, text in bundles.items():
        tokens = len(text) // 4
        if tokens > BUDGET[name]:
            problems.append("%s is ~%d tokens, over its %d budget: shorten the docs it includes" % (name, tokens, BUDGET[name]))
        path = out / name
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append("bundle/" + name)
        else:
            path.write_text(text, encoding="utf-8")
        print("%s ~%d tokens" % (name, tokens))
    if todo:
        problems.append("fields with no meaning written in the docs (fill in the TODO cells): " + ", ".join(todo))
    if uncovered:
        problems.append("schemas with no field table in docs/api: " + ", ".join(uncovered))
    if a.check and stale:
        problems.append("out of date (run: python3 tools/modkit.py bundle): " + ", ".join(stale))
    for p in problems:
        print("PROBLEM " + p)
    return 1 if problems else 0


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="modkit", description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog="\n".join(__doc__.split("\n")[3:]))
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("new", help="start a mod in mods/ID")
    s.add_argument("id", help="the mod id: one lowercase word, e.g. furhats")
    s.add_argument("--name", help="display name")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("new-def", help="copy a known-good def into a mod under a new id",
                       description="Copy an existing def (core or the mod's) as the start of a new one: KIND item, NAME fur_hat, "
                                   "--like core.item.tuque makes MOD.item.fur_hat in MOD/defs/items.json.")
    s.add_argument("kind", help="the kind: " + ", ".join(sorted(set(DOC_PAGES) - {"mod", "core.rooms", "core.colonist", "core.names", "core.worldgen", "core.rpg", "core.looks"})))
    s.add_argument("name", help="lowercase_name for the new id")
    s.add_argument("--like", required=True, help="the id to copy, e.g. core.item.tuque")
    s.add_argument("--mod", help="the mod (default: the only one in mods/)")
    s.set_defaults(fn=cmd_new_def)

    s = sub.add_parser("override", help="copy a core def whole into a mod, to change it",
                       description="Copy a def the mod loads on top of (e.g. core.biome.tundra) into MOD/defs/overrides.json, "
                                   "keeping its id, so the mod's copy replaces it.")
    s.add_argument("id", help="the id to override, e.g. core.biome.tundra")
    s.add_argument("--mod", help="the mod (default: the only one in mods/)")
    s.set_defaults(fn=cmd_override)

    s = sub.add_parser("validate", help="check a mod (no game needed)")
    s.add_argument("mod", nargs="?", help="mod folder or id")
    s.add_argument("--json", action="store_true", help="machine-readable report")
    s.add_argument("--local", action="store_true", help="skip the game's own check even if the game is found")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("test", help="run the game's validate + simulate (needs the game)")
    s.add_argument("mod", nargs="?")
    s.add_argument("--days", type=int)
    s.add_argument("--seeds", help="comma-separated, e.g. 1,2,3")
    s.add_argument("--biome", help="only land in this biome, e.g. core.biome.tundra")
    s.set_defaults(fn=cmd_test)

    s = sub.add_parser("sprite", help="preview a sprite")
    s.add_argument("sprite", help="a sprite id, or a .json file")
    s.add_argument("--id", help="with a file: only this sprite")
    s.add_argument("--mod", help="look the id up in this mod too")
    s.add_argument("--png", help="write a PNG instead (one per sprite/frame)")
    s.add_argument("--scale", type=int, default=8)
    s.add_argument("--main", default="#4f7cac", help="what $main shows as (the item's color)")
    s.add_argument("--skin", default="#e2b48f")
    s.add_argument("--hair", default="#4b3426")
    s.add_argument("--plain", action="store_true", help="no colors: # for filled pixels")
    s.add_argument("--over", help="draw it on top of this sprite, e.g. core.sprite.body for a worn layer, core.sprite.portrait.head for a portrait")
    s.set_defaults(fn=cmd_sprite)

    for name, fn, h in (("install", cmd_install, "copy into the game's mods folder and reload"),
                        ("uninstall", cmd_uninstall, "remove from the game's mods folder and reload"),
                        ("restore", cmd_restore, "put back the copy the last install replaced")):
        s = sub.add_parser(name, help=h)
        s.add_argument("mod")
        s.set_defaults(fn=fn)

    s = sub.add_parser("pack", help="validate and zip into dist/")
    s.add_argument("mod")
    s.set_defaults(fn=cmd_pack)

    s = sub.add_parser("bundle", help="rebuild bundle/ and generated docs")
    s.add_argument("--check", action="store_true", help="change nothing; exit 1 if anything is stale or undocumented")
    s.set_defaults(fn=cmd_bundle)

    s = sub.add_parser("sync", help="copy agents/ to .claude/agents/")
    s.set_defaults(fn=cmd_sync)

    s = sub.add_parser("doctor", help="find the game and the mods folder")
    s.set_defaults(fn=cmd_doctor)

    a = p.parse_args(argv)
    if not getattr(a, "fn", None):
        p.print_help()
        return 0
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
