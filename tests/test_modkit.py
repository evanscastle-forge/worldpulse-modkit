import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import modkit  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
BROKEN_ERRORS = sorted([
    "broken.animal.yeti diet", "broken.item.fur_hat Armor", "broken.item.fur_hat cold", "broken.item.fur_hat portrait",
    "broken.item.fur_hat recipe.item", "broken.item.fur_hat warmth", "broken.plant.moss None", "broken.sprite.hat rows",
    "broken.sprite.hat rows[0]",
])


def errors(report):
    return sorted("%s %s" % (i["def"], i["field"]) for i in report["issues"] if i["severity"] == "error")


class ValidateTests(unittest.TestCase):
    def test_core_content_is_clean(self):
        r = modkit.validate(ROOT / "reference" / "core")
        self.assertEqual([], [i for i in r["issues"] if i["severity"] != "note"])

    def test_examples_are_clean(self):
        for mod in sorted(p for p in (ROOT / "examples").iterdir() if p.is_dir()):
            with self.subTest(mod=mod.name):
                r = modkit.validate(mod)
                self.assertEqual([], [i for i in r["issues"] if i["severity"] in ("error", "warning")], modkit.format_report(r))

    def test_broken_fixture_names_each_mistake(self):
        r = modkit.validate(FIXTURES / "broken")
        self.assertEqual(BROKEN_ERRORS, errors(r))
        by_field = {i["field"]: i["message"] for i in r["issues"]}
        self.assertIn("did you mean 'core.item.leather'", by_field["recipe.item"])
        self.assertIn('write "armor"', by_field["Armor"])
        self.assertIn("unknown field", by_field["warmth"])

    @unittest.skipUnless(os.environ.get("WORLDPULSE_GAME"), "set WORLDPULSE_GAME to compare with the game's modtool")
    def test_agrees_with_the_game(self):
        for mod in [FIXTURES / "broken"] + sorted(p for p in (ROOT / "examples").iterdir() if p.is_dir()):
            with self.subTest(mod=mod.name):
                out = modkit.run_game(["modtool", "validate", str(mod), "--json"], capture=True).stdout
                game = json.loads(out)
                ours = modkit.validate(mod)
                key = lambda i: (i["severity"], i["def"], i["field"])
                self.assertEqual(sorted(map(key, game["issues"]), key=str), sorted(map(key, ours["issues"]), key=str))


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.old = modkit.MODS
        modkit.MODS = self.tmp
        self.addCleanup(setattr, modkit, "MODS", self.old)

    def test_new_then_new_def_then_override_validates(self):
        self.assertEqual(0, modkit.main(["new", "hats", "--name", "Hats"]))
        self.assertEqual(0, modkit.main(["new-def", "item", "fur_hat", "--like", "core.item.tuque", "--mod", "hats"]))
        self.assertEqual(0, modkit.main(["override", "core.biome.tundra", "--mod", "hats"]))
        r = modkit.validate(self.tmp / "hats")
        self.assertEqual([], errors(r))
        self.assertEqual(["core.biome.tundra"], r["overrides"])
        items = modkit.load_jsonc(self.tmp / "hats" / "defs" / "items.json")
        self.assertEqual("hats.item.fur_hat", items[0]["id"])

    def test_save_reply_writes_mod_files_only_and_expect_is_checked(self):
        modkit.main(["new", "pk"])
        reply = self.tmp / "reply.txt"
        reply.write_text("Here you go.\n\nmods/pk/defs/items.json\n```json\n[{\"id\": \"pk.item.pumpkin\", \"kind\": \"item\", \"nutrition\": 250, \"raw\": true}]\n```\n\n"
                         "mods/pk/tests/expect.json\n```json\n{\"expect\": [{\"metric\": \"sen\", \"id\": \"pk.item.pumpkin\"}]}\n```\n\n"
                         "mods/../tools/evil.py\n```\nx\n```\n")
        self.assertEqual(0, modkit.main(["save-reply", str(reply)]))
        self.assertTrue((self.tmp / "pk" / "defs" / "items.json").exists())
        self.assertFalse((ROOT / "tools" / "evil.py").exists())
        r = modkit.validate(self.tmp / "pk")
        self.assertIn("did you mean 'seen'", " ".join(i["message"] for i in r["issues"] if i["file"] == "tests/expect.json"))

    def test_sprite_png(self):
        out = self.tmp / "s.png"
        self.assertEqual(0, modkit.main(["sprite", "core.sprite.body", "--png", str(out), "--scale", "2", "--over", "core.sprite.body"]))
        self.assertTrue(out.read_bytes().startswith(b"\x89PNG"))

    def test_jsonc(self):
        self.assertEqual({"a": [1, 2], "b": "x // y"}, json.loads(modkit.strip_jsonc('{ "a": [1, 2,], /* c */ "b": "x // y", // d\n }')))


class BundleTests(unittest.TestCase):
    def test_docs_and_bundles_are_current_and_cover_every_field(self):
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "modkit.py"), "bundle", "--check"], capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
