# Build the original read-only native proof from pinned SHA256 guard fingerprints.
# Requires Python 3 and installed MinGW g++; logs stay in the selected build directory.
import argparse
import shutil
import subprocess
from pathlib import Path
from probe_native120_runtime import load_profiles


# Ship fingerprints rather than embedding proprietary game instruction sequences.
def build(root, output):
    output.mkdir(parents=True, exist_ok=True)
    profiles = load_profiles(root / "config/native120-profiles.json")
    if len(profiles) != 2:
        raise ValueError("Expected exactly two eleven-guard profiles")
    lines = ["// Generated SHA256 guards; never edit by hand.", "#pragma once", "struct Probe { SIZE_T rva; SIZE_T length; const unsigned char* digest; };"]
    for p, profile in enumerate(profiles):
        for i, probe in enumerate(profile["signatures"]):
            raw = bytes.fromhex(probe["expected_sha256"])
            rva = int(probe["game_rva"], 0)
            if probe["length"] > 2048:
                raise ValueError("Guard length mismatch")
            lines.append(f"static const unsigned char P{p}_{i}[] = {{{','.join(str(b) for b in raw)}}};")
    lines.append("static const Probe PROFILES[2][11] = {")
    for p, profile in enumerate(profiles):
        lines.append("{" + ",".join(f"{{{int(probe['game_rva'], 0)},{probe['length']},P{p}_{i}}}" for i, probe in enumerate(profile["signatures"])) + "},")
    lines.append("};")
    (output / "probes.h").write_text("\n".join(lines) + "\n", encoding="utf-8")
    compiler = shutil.which("g++")
    if not compiler:
        raise RuntimeError("MinGW g++ is missing; resolve the installed compiler before building")
    command = [compiler, "-std=c++17", "-O2", "-s", "-Wall", "-Wextra", "-Werror", "-shared", "-static-libgcc", "-static-libstdc++", "-Wl,--no-insert-timestamp,--image-base,0x180000000", "-I", str(output), str(root / "src/Diagnostics.cpp"), "-o", str(output / "WooDiagnostics.dll"), "-lcrypt32"]
    result = subprocess.run(command, text=True, capture_output=True)
    (output / "build.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Compiler failed ({result.returncode}); see {output / 'build.log'}")
    print(output / "WooDiagnostics.dll")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "build")
    args = parser.parse_args()
    build(Path(__file__).resolve().parents[1], args.output.resolve())
