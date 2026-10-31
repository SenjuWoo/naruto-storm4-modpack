# Verify the release checksum parser and asset comparison without network access.
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_release", ROOT / "tools/verify_release.py")
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class VerifyReleaseTests(unittest.TestCase):
    def test_checked_in_sums_parse(self):
        expected = module.parse_sums((ROOT / "release/SHA256SUMS.txt").read_text(encoding="utf-8"))
        self.assertEqual(len(expected), 2)
        self.assertIn("Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.001", expected)
        self.assertEqual(
            expected["Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.001"],
            "acb91537a3e80057126d864c2785bcfc418538648a373e0fdd3ef12b1038ab5d",
        )

    def test_parse_rejects_bad_hash(self):
        with self.assertRaises(ValueError):
            module.parse_sums("not-a-hash  file.7z.001\n")

    def test_parse_accepts_binary_marker(self):
        digest = "a" * 64
        self.assertEqual(module.parse_sums(f"{digest} *file.7z.001\n"), {"file.7z.001": digest})

    def test_compare_matches(self):
        digest = "a" * 64
        assets = [{"name": "file.7z.001", "digest": "sha256:" + digest}]
        self.assertEqual(module.compare_assets({"file.7z.001": digest}, assets), [])

    def test_compare_reports_missing_and_mismatch(self):
        digest = "a" * 64
        assets = [{"name": "other.7z.001", "digest": "sha256:" + "b" * 64}]
        errors = module.compare_assets({"file.7z.001": digest}, assets)
        self.assertTrue(any("missing" in error for error in errors))
        errors = module.compare_assets({"other.7z.001": digest}, assets)
        self.assertTrue(any("mismatch" in error for error in errors))

    def test_compare_ignores_extra_assets(self):
        digest = "a" * 64
        assets = [
            {"name": "file.7z.001", "digest": "sha256:" + digest},
            {"name": "SHA256SUMS.txt", "digest": "sha256:" + "c" * 64},
        ]
        self.assertEqual(module.compare_assets({"file.7z.001": digest}, assets), [])


if __name__ == "__main__":
    unittest.main()
