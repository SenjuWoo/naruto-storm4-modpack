# Package only the original diagnostic mod's runtime payload, never game/beta files.
# Build first; this deterministic archive is separate from the legacy modpack release.
from pathlib import Path
import zipfile

VERSION = "0.1.0"
MOD_ROOT = "moddingapi/mods/woo_diagnostics/"


# Fixed metadata makes identical DLLs and text produce identical upload archives.
def package(root):
    dll = (root / "build/WooDiagnostics.dll").read_bytes()
    if not dll:
        raise ValueError("Compiled diagnostic DLL is empty")
    files = {
        "WooDiagnostics.dll": dll,
        "info.txt": b"Woo Diagnostics|Read-only core-profile diagnostics; no FPS modification|SenjuWoo",
        "README.txt": (root / "docs/DIAGNOSTICS-README.txt").read_bytes(),
        "CHANGELOG.txt": (root / "docs/DIAGNOSTICS-CHANGELOG.txt").read_bytes(),
        "LICENSE.txt": (root / "src/LICENSE").read_bytes(),
    }
    output = root / "dist" / f"WooDiagnostics-{VERSION}.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(MOD_ROOT + name, date_time=(2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return output


if __name__ == "__main__":
    print(package(Path(__file__).resolve().parents[1]))
