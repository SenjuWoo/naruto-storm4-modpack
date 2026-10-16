# Verify the exact upload boundary and reproducibility without requiring a game install.
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("package", ROOT / "tools/package.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PackageTests(unittest.TestCase):
    def test_exact_payload_and_reproducible_bytes(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as folder:
            root = Path(folder)
            for child in ("build", "docs", "src"):
                (root / child).mkdir()
            (root / "build/WooDiagnostics.dll").write_bytes(b"native-dll-fixture")
            for name in ("DIAGNOSTICS-README.txt", "DIAGNOSTICS-CHANGELOG.txt"):
                (root / "docs" / name).write_text(name)
            (root / "src/LICENSE").write_text("original source license")
            output = module.package(root)
            before = output.read_bytes()
            self.assertEqual(module.package(root).read_bytes(), before)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), {module.MOD_ROOT + name for name in
                    ("WooDiagnostics.dll", "info.txt", "README.txt", "CHANGELOG.txt", "LICENSE.txt")})
                self.assertEqual(archive.read(module.MOD_ROOT + "WooDiagnostics.dll"), b"native-dll-fixture")
                self.assertFalse(archive.read(module.MOD_ROOT + "info.txt").endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
