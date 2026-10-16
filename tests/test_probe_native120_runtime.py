# Exercise signature acceptance, refusal, and real read-only Windows process boundaries.
# Tests write reports only into temporary directories; debug logging stays off.
import importlib.util
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "probe_native120_runtime.py"
SPEC = importlib.util.spec_from_file_location("probe_native120_runtime", MODULE_PATH)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def sample_profile():
    return {"profile_rva": "0x1000", "core_probe_count": 11,
            "signatures": [{"index": i, "game_rva": hex(i), "length": 1,
                            "expected_sha256": hashlib.sha256(b"\x90").hexdigest()} for i in range(11)]}


class ProbeTests(unittest.TestCase):
    def test_all_eleven_required(self):
        profile = sample_profile()
        matched = probe.compare_profiles([profile], 11, lambda rva, size: b"\x90")
        refused = probe.compare_profiles([profile], 11,
                                          lambda rva, size: b"\x91" if rva == 10 else b"\x90")
        self.assertTrue(matched["compatible"])
        first_probe = matched["profiles"][0]["probes"][0]
        self.assertEqual(set(first_probe), {"index", "rva", "length", "match", "actual_sha256"})
        self.assertEqual(first_probe["actual_sha256"], hashlib.sha256(b"\x90").hexdigest())
        self.assertFalse(refused["compatible"])
        self.assertEqual(refused["profiles"][0]["matches"], 10)

    def test_outside_module_is_never_read(self):
        def unexpected_read(rva, size):
            self.fail("An out-of-bounds read was attempted")
        result = probe.compare_profiles([sample_profile()], 0, unexpected_read)
        self.assertEqual(result["classification"], "incompatible")
        self.assertEqual(result["profiles"][0]["matches"], 0)

    def test_invalid_pid_rejected_before_api_access(self):
        for pid in (0, -1, 2**32):
            with self.assertRaisesRegex(ValueError, "PID"):
                with probe.open_process(pid, sys.executable):
                    self.fail("Invalid PID was accepted")

    def test_wrong_path_rejected(self):
        with self.assertRaisesRegex(ValueError, "image path differs"):
            probe.require_image(__file__, MODULE_PATH)

    def test_failure_report_is_written(self):
        profiles = Path(__file__).resolve().parents[1] / "config" / "native120-profiles.json"
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            self.assertTrue(Path(temporary).resolve().is_relative_to(Path(__file__).resolve().parent))
            output = Path(temporary) / "result.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = probe.main(["--pid", "0", "--image", sys.executable,
                                   "--profiles", str(profiles), "--output", str(output)])
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "error")
            self.assertIn("PID", result["cause"])
            self.assertEqual(result["version"], "0.1.0")

    def test_output_cannot_replace_an_input(self):
        with self.assertRaisesRegex(ValueError, "must differ"):
            probe.write_report(MODULE_PATH, {"config": {"image": str(MODULE_PATH),
                                                       "profiles": str(MODULE_PATH)}})

    def test_invalid_signature_metadata_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            self.assertTrue(Path(temporary).resolve().is_relative_to(Path(__file__).resolve().parent))
            path = Path(temporary) / "bad-profiles.json"
            invalid = [{"length": 0}, {"length": 4097}, {"length": True}, {"length": 1.0},
                       {"expected_sha256": "g" * 64}, {"expected_sha256": "a" * 63},
                       {"expected_sha256": "a" * 65}, {"expected_sha256": "A" * 64},
                       {"expected_sha256": None}]
            for metadata in invalid:
                with self.subTest(metadata=metadata):
                    profile = sample_profile()
                    profile["signatures"][0].update(metadata)
                    path.write_text(json.dumps({"profiles": [profile]}), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Invalid signature"):
                        probe.load_profiles(path)

    @unittest.skipUnless(os.name == "nt", "Windows process API required")
    def test_real_own_process_read_and_wrong_image_refusal(self):
        with probe.open_process(os.getpid(), sys._base_executable) as process:
            self.assertEqual(process["read_rva"](0, 2), b"MZ")
            with self.assertRaisesRegex(ValueError, "outside"):
                process["read_rva"](process["image_size"], 1)
        with self.assertRaisesRegex(ValueError, "image path differs"):
            with probe.open_process(os.getpid(), MODULE_PATH):
                self.fail("Wrong process image was accepted")


if __name__ == "__main__":
    unittest.main()
