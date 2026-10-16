# Exercise the compiled DLL in a real disposable Windows process, not a mocked loader.
# Its mapped .text must remain unchanged and report unsupported; this does not test gameplay.
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


class NativeProofTests(unittest.TestCase):
    # The quiet default must not create logs; the enabled report must reject this host.
    def test_real_loader_and_debug_toggle(self):
        root = Path(__file__).resolve().parents[1]
        dll = root / "build/WooDiagnostics.dll"
        interpreter = sys._base_executable
        before = hashlib.sha256(Path(interpreter).read_bytes()).hexdigest()
        # Read the child's mapped code, because a disk hash cannot detect runtime hooks.
        code = textwrap.dedent("""
            import ctypes, hashlib, json, os, struct, sys
            sys.path.insert(0, sys.argv[2])
            from probe_native120_runtime import open_process
            with open_process(os.getpid(), sys._base_executable) as process:
                read = process["read_rva"]
                dos = read(0, 64)
                assert dos[:2] == b"MZ"
                pe_offset = struct.unpack_from("<I", dos, 60)[0]
                pe = read(pe_offset, 24)
                assert pe[:4] == b"PE\\0\\0"
                section_count = struct.unpack_from("<H", pe, 6)[0]
                optional_size = struct.unpack_from("<H", pe, 20)[0]
                assert 1 <= section_count <= 96
                table = read(pe_offset + 24 + optional_size, section_count * 40)
                sections = [struct.unpack_from("<II", table, i * 40 + 8)
                            for i in range(section_count)
                            if table[i * 40:i * 40 + 8].rstrip(b"\\0") == b".text"]
                assert len(sections) == 1
                text_size, text_rva = sections[0]
                before = read(text_rva, text_size)
                dll = ctypes.WinDLL(sys.argv[1])
                dll.GameLoop.argtypes = [ctypes.c_longlong]
                dll.GameLoop.restype = None
                dll.GameLoop(0)
                dll.GameLoop(0)
                after = read(text_rva, text_size)
                print(json.dumps({"mapped_text_bytes": text_size,
                                  "before_sha256": hashlib.sha256(before).hexdigest(),
                                  "after_sha256": hashlib.sha256(after).hexdigest(),
                                  "mapped_text_unchanged": before == after}))
        """)
        proofs = []
        with tempfile.TemporaryDirectory(dir=root / "tests") as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(root / "tests"))
            report = Path(folder) / "SenjuWoo/Storm4Overhaul/logs/native-diagnostics.json"
            for debug in ("0", "1"):
                env = dict(os.environ, LOCALAPPDATA=folder, WOO_STORM4_DEBUG=debug)
                result = subprocess.run([interpreter, "-c", code, str(dll), str(root / "tools")],
                                        env=env, check=True, capture_output=True, text=True, timeout=20)
                proof = json.loads(result.stdout)
                self.assertGreater(proof["mapped_text_bytes"], 0)
                self.assertTrue(proof["mapped_text_unchanged"])
                self.assertEqual(proof["before_sha256"], proof["after_sha256"])
                proofs.append(dict(proof, debug=debug))
                if debug == "0":
                    self.assertFalse(report.exists())
            data = json.loads(report.read_text())
            self.assertEqual(data["version"], "0.1.0")
            self.assertEqual(data["profile_matches"], [0, 0])
            self.assertFalse(data["core_profile_candidate"])
            self.assertFalse(data["gameplay_validated"])
            self.assertTrue(data["read_only"])
            for p in range(2):
                self.assertEqual(data["profile_readable"][p] + data["profile_out_of_bounds"][p] + data["profile_probe_failures"][p], 11)
        self.assertEqual(before, hashlib.sha256(Path(interpreter).read_bytes()).hexdigest())
        print(json.dumps({"native_host_memory_proofs": proofs}))


if __name__ == "__main__":
    unittest.main()
