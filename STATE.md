# State

Updated 2026-11-08. Original diagnostics component: 0.1.0. Stable native 120 FPS Free Battle is **not working**; the beta activation path still refuses.

Live install is restored and verified: `NSUNS4.exe` SHA-256 `147e52a3...`, root `d3dcompiler_47.dll` = `d3dcompiler_47.api.bak` = `5e486da4...`, `config.ini` restored from `config.ini.pre120` (`vsync=1`, no `fps=120`). No Storm 4 process remains.

Implemented: read-only native loader proof, SHA-256-only core fingerprints, exact-PID/path runtime probe, tests and payload packaging. Existing pack loader and genuine compiler are retained. The 2026-11-07 static map found all 11 core spans and 7 hook bodies in the installed image, with non-uniform deltas.

The 2026-11-08 activation attempt rebuilt the beta's profile-0 core/hook tables and hardcoded hook starts, but the beta loaded and wrote **zero** hook stubs. Selecting the alternate profile wrote 17 jumps at old addresses and was rejected. The five timing constants at their correct live RVAs still showed 58-59 FPS on the title/opening screen with `vsync=0`; no Free Battle measurement exists. Remaining blocker: the beta's `FUN_180001260` guard/profile activation path, specifically the 15-entry profile-0 guard table at `0x1800013ac`. Next experiment is to map those guard entries to the installed image, not to bypass them.

Last good gameplay source: original supplied pack and live install, preserved. This repository's diagnostic component changes no gameplay. The isolated experiment was closed and the live config restored. Live EXE, compiler DLLs, config and save hashes remained unchanged.

Next: map the beta's 15 profile-0 guard entries to the installed layout and re-test activation; only then attempt a Free Battle and measure restarted 30/60/120 baselines and the regression matrix in [BENCHMARKS.md](BENCHMARKS.md). Do not force the incompatible beta guards or build later content features on an unvalidated timing foundation.

Build/test/package commands are in [BUILD.md](BUILD.md). Logs and rollback are in [INSTALL.md](INSTALL.md). Private machine paths, backups and runtime receipts remain in the local owner folder outside public source. Source CI/release receipts must be verified on the exact pushed SHA; diagnostic publication cannot mark the gameplay goal complete.

## Repository tooling (2026-11-08)

- Replaced the 99-byte LICENSE stub with valid MIT text; GitHub license detection now reports MIT, and the scope is documented in the README.
- Added author-level [CREDITS.md](CREDITS.md) transcribed from the archive's `Credits.txt`; it does not claim a file-by-file mapping.
- Added `release/SHA256SUMS.txt` for the two v1.0.0 volumes and `tools/verify_release.py`. The downloaded release bytes matched the pinned hashes on 2026-10-31.
- Added `scripts/WooPack.ps1` with `Install.bat`/`Uninstall.bat`: backup, SHA-256 manifest, rollback, `.woopack-displaced` preservation, and `\\?\` long-path handling. The uninstaller now validates the manifest schema and every relative path, refuses source/game overlap and an unowned backup folder, preflights all required backups, and keeps the manifest plus backups when a rollback is incomplete. **29 tests pass**, including four new failure-injection cases.
- `Install.bat`/`Uninstall.bat` now fail clearly when `scripts\WooPack.ps1` is missing; README install steps tell users to keep the folder together.
- Diagnostics source, version, and gameplay claims are unchanged. No 120 FPS or combat result is claimed.
