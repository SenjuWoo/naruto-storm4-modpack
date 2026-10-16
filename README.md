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
  <a href="https://github.com/SenjuWoo/naruto-storm4-modpack/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/release-v1.0.0%207z-53d7ff?labelColor=140b07" alt="v1.0.0 7z"></a>
  <img src="https://img.shields.io/badge/game-not%20included-e23d2b?labelColor=140b07" alt="Game not included">
</p>

<p align="center">
  <a href="https://github.com/SenjuWoo/naruto-storm4-modpack/releases/tag/v1.0.0">Release v1.0.0</a>
  ·
  <a href="NOTES.md">Notes</a>
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
- `My save/STORM4.S` — a **personal save** (130&nbsp;KB). Review it before you keep or share it.
- Verified layout: 5,841 files, 427 folders, 9.29&nbsp;GB uncompressed
- Compressed 7z: 2,221,758,792 bytes (two volumes × 1,110,879,396 bytes)
- Archive test recorded in notes: `7z t` → `Everything is Ok`

The game itself is **not** included.

## Download the archive

The git tree will never contain the pack. GitHub Release **[v1.0.0](https://github.com/SenjuWoo/naruto-storm4-modpack/releases/tag/v1.0.0)** attaches a split 7z because a single file would exceed the 2&nbsp;GB release-asset cap.

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

Other mirrors and a local zip pointer (not in git) are listed in [`NOTES.md`](NOTES.md).

## Project map

```text
README.md     this file
NOTES.md      release notes, archive sizes, save-file warning
LICENSE       docs license; each mod keeps its author’s terms
docs/images/  pack mark only
```

The diagnostics payload is built separately from the legacy archive. It contains only its own `moddingapi/mods/woo_diagnostics` folder.

## Honest status

Verified:

- original diagnostics build and test evidence is recorded in TEST_RESULTS.md
- v1.0.0 release assets exist at the names and byte sizes above
- notes record 5,841 files / 427 folders / `7z t` OK

Not claimed:

- the archive is inside `git clone`
- a first-party character-by-character credits table (this pack is a personal/community bundle — see NOTES)
- in-game screenshots
- stable 120 FPS or a completed gameplay overhaul
- affiliation with Bandai Namco, CyberConnect2, Shueisha, or TV Tokyo

## Credits

Personal / community modpack. Individual `.xfbin` mods remain the property of their original authors. See [`NOTES.md`](NOTES.md).

Naruto, Naruto Shippuden, and Ultimate Ninja Storm 4 are trademarks of their owners. This project is unofficial.

## License

The documentation files in this repository are under the terms in [`LICENSE`](LICENSE). That is **not** a license to the game or to every mod inside the archive. Each mod keeps its original author’s license.
