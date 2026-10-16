# Exercise the native hash, mismatch, bounds and unreadable-memory branches directly.
# Python supplies an independent SHA256 oracle; the test executable never ships.
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class NativeCheckTests(unittest.TestCase):
    def test_native_guard_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        digest = ",".join(str(b) for b in hashlib.sha256(b"abc").digest())
        code = '''#include "Diagnostics.cpp"
#include <cassert>
int main() {
    unsigned char input[] = {'a','b','c'};
    unsigned char expected[] = {DIGEST};
    Probe guard{0, 3, expected}; DWORD error{};
    assert(Check(input, 3, guard, error) == 1);
    input[0] = 'd'; assert(Check(input, 3, guard, error) == 0);
    guard.rva = 3; assert(Check(input, 3, guard, error) == 2);
    guard.rva = 0;
    auto* blocked = static_cast<unsigned char*>(VirtualAlloc(nullptr, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_NOACCESS));
    assert(blocked); assert(Check(blocked, 4096, guard, error) == -1); assert(error != 0);
    assert(VirtualFree(blocked, 0, MEM_RELEASE));
}
'''.replace("DIGEST", digest)
        with tempfile.TemporaryDirectory(dir=root / "tests") as folder:
            source = Path(folder) / "native_test.cpp"
            binary = Path(folder) / "native_test.exe"
            source.write_text(code, encoding="utf-8")
            command = [shutil.which("g++") or "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-static-libgcc", "-static-libstdc++", "-I", str(root / "src"), "-I", str(root / "build"), str(source), "-o", str(binary), "-lcrypt32"]
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
            subprocess.run([str(binary)], check=True, timeout=20)


if __name__ == "__main__":
    unittest.main()
