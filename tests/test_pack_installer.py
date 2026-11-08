# Exercise the transactional installer against a disposable mock game.
# The test needs Windows PowerShell and never touches a real Storm 4 install.
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "WooPack.ps1"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "Windows PowerShell is required")
class PackInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tests")
        self.root = Path(self.temp.name)
        self.game = self.root / "game"
        self.source = self.root / "src"
        write(self.game / "NSUNS4.exe", b"game-exe")
        write(self.game / "config.ini", b"vanilla-config")
        write(self.game / "data/patch/12/sound.cpk", b"vanilla-sound")
        write(self.game / "data/launch/movie1.cpk", b"vanilla-movie")
        write(self.source / "moddingapi/config.ini", b"pack-config")
        write(self.source / "data/patch/12/sound.cpk", b"pack-sound")
        write(self.source / "data/launch/movie1.cpk", b"pack-movie")
        write(self.source / "data_win32/effect/test.xfbin", b"pack-effect")
        write(self.source / "character/s3sk/awacombos.xfbin", b"pack-char")
        write(self.source / "d3dcompiler_47.dll", b"pack-dll")
        write(self.source / "d3dcompiler_47_o.dll", b"pack-dll-o")
        write(self.source / "Save File/STORM4.S", b"personal-save")
        write(self.source / "Credits.txt", b"credits")
        write(self.source / "Installation_Instructions.txt", b"instructions")

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, action, game=None, source=None, extra=()):
        command = [
            POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
            "-Action", action,
            "-GamePath", str(game or self.game),
            "-LogPath", str(self.root / "install.log"),
        ]
        if source is not None:
            command += ["-SourcePath", str(source)]
        command += list(extra)
        return subprocess.run(command, capture_output=True, text=True)

    def test_install_backs_up_and_skips_save_and_docs(self):
        result = self.run_script("Install", source=self.source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.game / ".woopack-manifest.json").exists())
        self.assertEqual((self.game / "_WooPack_Backup/data/patch/12/sound.cpk").read_bytes(), b"vanilla-sound")
        self.assertEqual((self.game / "_WooPack_Backup/data/launch/movie1.cpk").read_bytes(), b"vanilla-movie")
        self.assertEqual((self.game / "data/patch/12/sound.cpk").read_bytes(), b"pack-sound")
        self.assertEqual((self.game / "data/launch/movie1.cpk").read_bytes(), b"pack-movie")
        self.assertEqual((self.game / "moddingapi/config.ini").read_bytes(), b"pack-config")
        self.assertEqual((self.game / "character/s3sk/awacombos.xfbin").read_bytes(), b"pack-char")
        self.assertEqual((self.game / "data_win32/effect/test.xfbin").read_bytes(), b"pack-effect")
        self.assertEqual((self.game / "d3dcompiler_47.dll").read_bytes(), b"pack-dll")
        self.assertFalse((self.game / "Save File/STORM4.S").exists())
        self.assertFalse((self.game / "Credits.txt").exists())
        self.assertFalse((self.game / "Installation_Instructions.txt").exists())
        self.assertEqual((self.game / "config.ini").read_bytes(), b"vanilla-config")

    def test_uninstall_restores_and_preserves_edit(self):
        self.assertEqual(self.run_script("Install", source=self.source).returncode, 0)
        (self.game / "moddingapi/config.ini").write_bytes(b"user-edit")
        result = self.run_script("Uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.game / "data/patch/12/sound.cpk").read_bytes(), b"vanilla-sound")
        self.assertEqual((self.game / "data/launch/movie1.cpk").read_bytes(), b"vanilla-movie")
        self.assertEqual((self.game / "moddingapi/config.ini.woopack-displaced").read_bytes(), b"user-edit")
        self.assertFalse((self.game / "moddingapi/config.ini").exists())
        self.assertFalse((self.game / "character/s3sk/awacombos.xfbin").exists())
        self.assertFalse((self.game / "data_win32/effect/test.xfbin").exists())
        self.assertFalse((self.game / "_WooPack_Backup").exists())
        self.assertFalse((self.game / ".woopack-manifest.json").exists())
        self.assertEqual((self.game / "NSUNS4.exe").read_bytes(), b"game-exe")
        self.assertEqual((self.game / "config.ini").read_bytes(), b"vanilla-config")

    def test_refuses_missing_game_exe(self):
        (self.game / "NSUNS4.exe").unlink()
        result = self.run_script("Install", source=self.source)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.game / ".woopack-manifest.json").exists())

    def test_refuses_second_install(self):
        self.assertEqual(self.run_script("Install", source=self.source).returncode, 0)
        result = self.run_script("Install", source=self.source)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.game / ".woopack-manifest.json").exists())
        self.assertEqual((self.game / "moddingapi/config.ini").read_bytes(), b"pack-config")

    def test_accepts_parent_of_pack_folder(self):
        parent = self.root / "extracted"
        parent.mkdir()
        shutil.move(str(self.source), str(parent / "Naruto To Boruto 2.0"))
        result = self.run_script("Install", source=parent)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.game / ".woopack-manifest.json").exists())

    def test_uninstall_recovers_interrupted_install(self):
        digest = lambda data: hashlib.sha256(data).hexdigest()
        manifest = {
            "schema": 2,
            "pack": "test",
            "state": "installing",
            "game_path": str(self.game),
            "source_path": str(self.source),
            "files": [
                {"path": "data\\patch\\12\\sound.cpk", "sha256": digest(b"pack-sound"), "size": 10, "had_backup": True},
                {"path": "data\\launch\\movie1.cpk", "sha256": digest(b"pack-movie"), "size": 10, "had_backup": True},
                {"path": "character\\s3sk\\awacombos.xfbin", "sha256": digest(b"pack-char"), "size": 9, "had_backup": False},
                {"path": "moddingapi\\config.ini", "sha256": digest(b"pack-config"), "size": 11, "had_backup": False},
            ],
            "backups": [
                {"path": "data\\patch\\12\\sound.cpk", "sha256": digest(b"vanilla-sound"), "size": 13},
                {"path": "data\\launch\\movie1.cpk", "sha256": digest(b"vanilla-movie"), "size": 13},
            ],
        }
        write(self.game / "_WooPack_Backup/data/patch/12/sound.cpk", b"vanilla-sound")
        write(self.game / "data/patch/12/sound.cpk", b"pack-sound")
        write(self.game / "character/s3sk/awacombos.xfbin", b"pack-char")
        write(self.game / ".woopack-manifest.json", json.dumps(manifest).encode())
        result = self.run_script("Uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.game / "data/patch/12/sound.cpk").read_bytes(), b"vanilla-sound")
        self.assertEqual((self.game / "data/launch/movie1.cpk").read_bytes(), b"vanilla-movie")
        self.assertFalse((self.game / "character/s3sk/awacombos.xfbin").exists())
        self.assertFalse((self.game / "moddingapi/config.ini").exists())
        self.assertFalse((self.game / "_WooPack_Backup").exists())
        self.assertFalse((self.game / ".woopack-manifest.json").exists())

    def test_uninstall_missing_backup_aborts_and_keeps_manifest(self):
        self.assertEqual(self.run_script("Install", source=self.source).returncode, 0)
        (self.game / "_WooPack_Backup/data/launch/movie1.cpk").unlink()
        result = self.run_script("Uninstall")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.game / ".woopack-manifest.json").exists())
        self.assertTrue((self.game / "_WooPack_Backup").exists())
        self.assertEqual((self.game / "data/launch/movie1.cpk").read_bytes(), b"pack-movie")

    def test_uninstall_rejects_path_escape(self):
        self.assertEqual(self.run_script("Install", source=self.source).returncode, 0)
        manifest_path = self.game / ".woopack-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][0]["path"] = "..\\outside.txt"
        manifest_path.write_text(json.dumps(manifest))
        outside = self.root / "outside.txt"
        outside.write_bytes(b"do-not-touch")
        result = self.run_script("Uninstall")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outside.read_bytes(), b"do-not-touch")
        self.assertTrue(manifest_path.exists())

    def test_refuses_unowned_backup_folder(self):
        write(self.game / "_WooPack_Backup/unrelated.bin", b"keep")
        result = self.run_script("Install", source=self.source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.game / "_WooPack_Backup/unrelated.bin").read_bytes(), b"keep")
        self.assertFalse((self.game / ".woopack-manifest.json").exists())

    def test_refuses_source_inside_game(self):
        nested = self.game / "_src"
        write(nested / "moddingapi/config.ini", b"pack-config")
        result = self.run_script("Install", source=nested)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.game / ".woopack-manifest.json").exists())

    def test_dry_run_writes_nothing(self):
        result = self.run_script("Install", source=self.source, extra=("-DryRun",))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.game / ".woopack-manifest.json").exists())
        self.assertEqual((self.game / "data/patch/12/sound.cpk").read_bytes(), b"vanilla-sound")

    def test_uninstall_without_manifest_fails(self):
        result = self.run_script("Uninstall")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
