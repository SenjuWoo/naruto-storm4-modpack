<p align="center">
  <img src="docs/images/mark.svg" width="72" height="72" alt="Naruto Storm 4 Woo Modpack mark">
</p>

<h1 align="center">Naruto Storm 4 — Woo Modpack</h1>

<p align="center"><strong>Community modpack archive and original overhaul diagnostics.</strong></p>

<p align="center">
  This git repository does <strong>not</strong> contain the playable archive.<br>
  The legacy archive is 2,221,758,792 bytes compressed and remains on Releases.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/repo-docs%20%2B%20attribution-ff7a18?labelColor=140b07" alt="Docs and attribution">
  <img src="https://img.shields.io/badge/archive-not%20in%20git-8f9aa6?labelColor=140b07" alt="Archive not in git">
  <a href="https://github.com/SenjuWoo/naruto-storm4-modpack/releases/latest"><img src="https://img.shields.io/github/v/release/SenjuWoo/naruto-storm4-modpack?label=release&color=53d7ff&labelColor=140b07" alt="latest release"></a>
  <img src="https://img.shields.io/badge/game-not%20included-e23d2b?labelColor=140b07" alt="Game not included">
</p>

<p align="center">
  <a href="https://github.com/SenjuWoo/naruto-storm4-modpack/releases/tag/v1.0.0">Release v1.0.0</a>
  ·
  <a href="NOTES.md">Notes</a>
  ·
  <a href="CREDITS.md">Credits</a>
  ·
  <a href="#honest-status">Honest status</a>
</p>

No in-game screenshots are shipped here. The mark is original pack branding, not a Bandai Namco / Shueisha / TV Tokyo asset.

## Overhaul development

The original **Woo Diagnostics** component builds a read-only native plugin and an explicit-PID runtime probe. It preserves the existing pack loader and genuine compiler. It does not unlock FPS or change combat.

In an isolated copy of the inspected game, the supplied Native120 beta loaded separately without replacing either compiler DLL. Both of its core profiles matched **0/11** required spans in the running game. All 22 spans were readable. A loaded beta is therefore not evidence of working 120 FPS on this executable.

Build and test on Windows x64 with Python 3.11+ and MinGW g++:

```text
python tools/build.py
python -m unittest discover -s tests -v
```

See [test results](TEST_RESULTS.md), [build instructions](BUILD.md), [installation and rollback](INSTALL.md), and the [roadmap](ROADMAP.md). Native logging is quiet by default; `WOO_STORM4_DEBUG=1` enables the report described in INSTALL.md. Original diagnostics source is under the [MIT license](src/LICENSE). Game files, the beta and legacy third-party mods are not covered by that grant.

## Why this repo is small

This repository contains original diagnostics source/tests and the legacy pack's documentation and attribution. Game files and third-party mod binaries stay out of the Git tree.

```text
this repo     original diagnostics source/tests, research, legacy notes
not in git    the .xfbin pack (5,841 files / 427 folders)
on Releases   split 7z, two parts, for people who want the archive
you provide   Naruto Shippuden: Ultimate Ninja Storm 4 (PC)
```

## What’s in the archive (not in this clone)

From [`NOTES.md`](NOTES.md) and the v1.0.0 release notes:

- Storm 4 mod files (`.xfbin`) — effects, skills, sound, characters
- `My save/STORM4.S` — a **personal save** (130&nbsp;KB). The archive also contains `Naruto To Boruto 2.0/Save File/STORM4.S` (same size). Review both before you keep or share them; the installer does not copy either one.
- Verified layout: 5,841 files, 427 folders, 9.29&nbsp;GB uncompressed
- Compressed 7z: 2,221,758,792 bytes (two volumes × 1,110,879,396 bytes)
- Archive test recorded in notes: `7z t` → `Everything is Ok`

The game itself is **not** included.

## Download the archive

The git tree will never contain the pack. GitHub Release **[v1.0.0](https://github.com/SenjuWoo/naruto-storm4-modpack/releases/tag/v1.0.0)** attaches a split 7z and `SHA256SUMS.txt` because a single file would exceed the 2&nbsp;GB release-asset cap.

1. Download **both** parts into the same folder:
   - `Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.001` (1,110,879,396 bytes)
   - `Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.002` (1,110,879,396 bytes)
2. Extract the first part. 7-Zip follows `.002` automatically.

```bat
:: Windows — 7-Zip on PATH
7z x "Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.001"
```

```sh
# macOS / Linux — p7zip
7z x "Naruto.Shippuden.Ultimate.Ninja.Storm.4.Woomodpack-2.7z.001"
```

Other mirrors are listed in [`NOTES.md`](NOTES.md).

## Install and rollback

The archive is a loose-file overlay, not a mod-manager build. You can install it manually or with the transactional installer in this repository.

### Transactional installer

1. Download both volumes and extract the first one to a folder outside the game. 7-Zip follows `.002`; you get a `Naruto To Boruto 2.0` folder.
2. Close Storm 4.
3. Download the repository ZIP (or at least keep `Install.bat`, `Uninstall.bat`, and `scripts\WooPack.ps1` together in the same folder). The batch files are not inside the legacy archive; if `scripts\WooPack.ps1` is missing they stop with a clear message instead of a PowerShell error.
4. Run `Install.bat` and point it at the extracted `Naruto To Boruto 2.0` folder. It auto-detects the Steam library, or pass the game folder explicitly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\WooPack.ps1 `
  -Action Install `
  -SourcePath "D:\Downloads\Naruto To Boruto 2.0"
```

The installer copies only `character\`, `data\`, `data_win32\`, `moddingapi\`, and the two compiler DLLs. It does **not** install `Save File\STORM4.S`, `Credits.txt`, or `Installation_Instructions.txt`. Before replacing any existing file it moves the original into `_WooPack_Backup\` and records its SHA-256 in `.woopack-manifest.json`. A missing `NSUNS4.exe`, an existing manifest, or insufficient free space aborts before touching the game folder; budget roughly the pack size plus the size of the files it replaces. `-DryRun` prints the plan without writing.

To roll back, close the game and run `Uninstall.bat` (or `-Action Uninstall`). It removes the pack-owned files, restores every backup, verifies the restored SHA-256, and preserves a file you edited after installation as `<name>.woopack-displaced`. The manifest is written before the first file copy, so an interrupted install can still be rolled back with the same command. If a required backup is missing or corrupt, rollback stops before changing game files and keeps the manifest plus recoverable backups; it never reports success for a partial restore. A pre-existing `_WooPack_Backup` folder without a WooPack manifest is treated as unowned and is never overwritten or deleted.

The installer is fixture-tested in CI. A full install from the 2.2&nbsp;GB release archive is not part of CI, so keep your own backup for a first install.

### Manual install

The legacy instructions still work: extract the archive and drag `character`, `data`, `data_win32`, `moddingapi`, `d3dcompiler_47.dll`, and `d3dcompiler_47_o.dll` into the game folder, confirming replacements. Do not copy `Save File\STORM4.S` unless you intend to replace your save.

### Manual rollback

Steam's **Verify integrity of game files** restores files Steam tracks, including the replaced `data\launch\movie1.cpk` and `data\patch\12\sound.cpk`. It does **not** delete untracked pack files such as `moddingapi\` or loose `data_win32\` overrides. Back up the game folder before a manual install; the transactional installer exists because there is no reliable one-click undo for a drag-and-drop install.

## Troubleshooting

| Symptom | Check |
|---|---|
| Modder console appears | The 2021 API ships `EnableConsole=1` for modders. Set `EnableConsole=0` in `moddingapi\config.ini`. |
| Startup crash after adding mods | If you use the NSUNS4 Mod Manager, an empty extracted mod folder in `moddingapi\` can crash the game; remove it. The upstream v0.6 release fixed that class of crash. |
| Extraction fails on a deeply nested path | Extract to a short root such as `C:\NS4`; the upstream Mod Manager v0.5.4 added `\\?\` long-path handling. |
| DLC missing on the menu despite being installed | Steam App 349040 has a reported client-side DLC recognition bug; check [steam-for-linux #11946](https://github.com/ValveSoftware/steam-for-linux/issues/11946) and the Steam client channel before changing game files. |
| First Ultimate Jutsu or Restart Battle crashes with custom fighters | These are documented engine hazards for extra fighters, not pack-install problems; see the [Universal Modder field notes](https://universal-modder.dev/games/naruto-shippuden-ultimate-ninja-storm-4). |

## Project map

```text
README.md     this file
NOTES.md      release notes, archive sizes, save-file warning
CREDITS.md    author-level attribution from the archive
LICENSE       MIT for original repo content; mods keep their authors’ terms
INSTALL.md    diagnostics install/rollback, not the legacy pack
release/      SHA256SUMS.txt and release verification notes
scripts/      transactional pack installer/uninstaller
tools/        build, package, probe and release verification
docs/images/  pack mark only
```

The diagnostics payload is built separately from the legacy archive. It contains only its own `moddingapi/mods/woo_diagnostics` folder.

## Honest status

Verified:

- original diagnostics build and test evidence is recorded in TEST_RESULTS.md
- v1.0.0 release assets exist at the names and byte sizes above; their SHA-256 hashes are pinned in [`release/SHA256SUMS.txt`](release/SHA256SUMS.txt) and were checked against the downloaded bytes on 2026-10-31
- notes record 5,841 files / 427 folders / `7z t` OK
- author-level credits are transcribed from the archive's `Credits.txt` in [`CREDITS.md`](CREDITS.md)
- the transactional installer/uninstaller passes 29 Windows fixture tests, including backup, restore, `.woopack-displaced` preservation, missing-backup abort, path-escape rejection and unowned-backup refusal; an incomplete rollback keeps the manifest and recoverable backups

Not claimed:

- the archive is inside `git clone`
- a file-by-file credits mapping (the archive records authors, not which `.xfbin` belongs to whom)
- in-game screenshots
- stable 120 FPS or a completed gameplay overhaul
- a full installer run against every real game build or the complete 2.2&nbsp;GB archive in CI
- online multiplayer matchmaking compatibility while modded
- affiliation with Bandai Namco, CyberConnect2, Shueisha, or TV Tokyo

## Credits

Personal / community modpack. Individual `.xfbin` mods remain the property of their original authors. See [`CREDITS.md`](CREDITS.md) for the author-level list transcribed from the archive, and [`NOTES.md`](NOTES.md) for release notes.

Naruto, Naruto Shippuden, and Ultimate Ninja Storm 4 are trademarks of their owners. This project is unofficial.

## License

The original documentation, installer/tooling, tests, and build scripts in this repository are MIT-licensed under [`LICENSE`](LICENSE). The diagnostics source under `src/` has its own MIT license at [`src/LICENSE`](src/LICENSE). Neither license covers the game or the third-party mods in the archive; each mod keeps its author’s terms.
