# Research record

Snapshot: 0.1.0. Upstream observations: 2026-10-15. Local runtime observations: 2026-10-16. This document reuses the upstream observations; it does not claim an upstream refresh on 2026-10-16.

The current deliverable is original, read-only compatibility diagnostics and a development record. It is not a playable overhaul or a 120 FPS fix. Game-load, battle, timing, visual and performance proof must be recorded separately in `TEST_RESULTS.md` and [BENCHMARKS.md](BENCHMARKS.md).

## Evidence and limits

Observed file bytes and source code take precedence over project descriptions. A source mechanism establishes an implementation route, not gameplay correctness. Successful DLL loading does not establish that any beta patch applied. A match against all core probes would establish only a core-profile candidate; later patch guards and gameplay still need checking.

The local static analysis record is `evidence/native120-profiles.json`. It was captured on 2026-10-15 with read-only PE section/RVA translation, embedded-table extraction and installed disassembly tools. Raw machine-specific input paths and instruction bytes remain private evidence. The public [config/native120-profiles.json](config/native120-profiles.json) uses schema 2: ordered RVAs, span lengths and `expected_sha256` fingerprints only, without game instruction bytes.

| Inspected input | SHA-256 | Size |
|---|---|---:|
| Supplied Native120 0.2.0-beta1 DLL | `dfb9706e17892cd0d9cad7fb4378e1e15981e8245361711f9b7ab51b6e181651` | 188,416 bytes |
| Installed Storm 4 executable, on disk | `147e52a3e0d7382501a6777e158b37908e0b69d4e902079dc6e62dcae69bc257` | 24,686,592 bytes |
| Preserved genuine compiler `_o` | `e994847e01a6f1e4cbdc5a864616ac262f67ee4f14db194984661a8d927ab7f4` | 4,173,928 bytes |

The inspected beta and game executable are AMD64 PE32+ binaries. These hashes identify this analysis set, not every Steam installation or every file described as Storm 4 1.09.

## Native120 findings

[HenDGS Native 120 FPS, Nexus 672](https://www.nexusmods.com/narutoultimateninjastorm4/mods/672) published 0.2.0-beta1, last updated 2026-10-06, when observed. The author describes experimental Free Battle support, primarily tested with EVO and also intended for the normal game. Story Mode and online are unsupported.

The documented corrections concern jump delivery and impulses, movement entry/cadence, dash acceleration and braking, steering geometry, cached motion across physics/contact changes, and aerial camera timing. The author explicitly leaves landing/collision integration, combat timing and broader live gameplay coverage unfinished. Earlier menu, character-selection and jutsu-customization input patches are excluded from this beta. Retained reports include input delay, an aerial finisher miss, EVO relay timing differences and a long match timer. These reports are retest targets, not reproduced failures of this snapshot.

The published procedure requires the genuine compiler as `D3DCompiler_47_o.dll`, the beta proxy as `D3DCompiler_47.dll`, and the game's own `fps=120` followed by restart. For comparisons, change the game setting and restart each time; externally limiting a running 120 FPS session is not an equivalent baseline. These are upstream instructions, not instructions to overwrite an existing pack loader.

### What the supplied binary establishes

The inspected beta has 29 PE export forwarders, all targeting corresponding exports in `d3dcompiler_47_o`. Its process-attach path checks the main image's PE identity and calls a patch routine; it can return success even when no patch applies. No self-filename check was observed in that inspected path. The later controlled side-load below verifies discovery/loading of this unchanged binary; it does not establish compatible timing patches.

| Embedded core profile table RVA | Required probes | Matches at expected RVAs in the on-disk executable |
|---|---:|---:|
| `0x16370` | 11 | 0 |
| `0x163f8` | 11 | 0 |

Two shared byte sequences occur elsewhere in the inspected executable, at RVAs `0xA0C29A` and `0x9E1320`. This is consistent with a different executable layout; it does not establish a safe uniform relocation. Long function bodies, relative calls, state offsets and later guards cannot be corrected by guessing a common offset.

These static results alone did not establish the live-image outcome. Runtime bytes can differ from disk. The initialized copied-game observation below now establishes the same mismatch in that running image; it does not generalize to every executable or prove beta patch execution.

### Initialized copied-game observation, 2026-10-16

The isolated copied game started and rendered its intro, then displayed an installed-mod list with nine entries including Woo Diagnostics. The root pack API, preserved genuine `_o` compiler and original diagnostics DLL were present in the process. This is native loader/callback integration proof, not a battle or performance result.

The native report found profile matches `[0,0]`, readable spans `[11,11]`, out-of-bounds spans `[0,0]` and probe failures `[0,0]`. An independent external probe completed all 22 reads and also found 0/11 for each profile; its private receipt is `evidence/native120-runtime-desktop.json`.

**Both extracted core profiles are incompatible with the initialized copied-game image observed in this initial test.** Native120 itself was not staged or loaded for that initial observation. No FPS, normal-speed combat or gameplay stability claim follows from the successful intro or mod list.

### Controlled separate beta loading, 2026-10-16

A subsequent initialized copied-game process loaded exactly one unchanged beta as `Native120.dll` from its own mod folder alongside the SHA-256-only `WooDiagnostics.dll`. The original pack proxy and genuine `_o` compiler remained loaded and their hashes were unchanged. This verifies direct separate loading without an adapter or root-proxy replacement.

The native receipt, `evidence/native-side-load.json`, reports `native120_module_loaded=true`, matches `[0,0]`, readable spans `[11,11]`, out-of-bounds/probe failures `[0,0]` and first probe error 0. The independent SHA-256-only external receipt, `evidence/native120-runtime-side-load.json`, reports status `ok`, classification `incompatible`, exit code 3, and 22 successfully read mismatching spans.

Separate loading is therefore completed; core-profile incompatibility/refusal remains the outcome for this image. This does not prove any timing correction applied. `fps=120` was requested only in the isolated lab configuration. Presented FPS, normal gameplay speed, battle behavior and sustained stability were not measured. Current-build timing support and measured Free Battle baselines/regressions remain unfinished. Keep the unsupported beta disabled outside deliberate compatibility experiments.

### Compiler chain constraint

The pack loader and the beta both claim the root compiler-proxy name. Preserve the pack's loader and the genuine compiler. Renaming the beta to `D3DCompiler_47_o.dll` would make its forwarded compiler exports resolve back through that same beta module rather than the genuine compiler. That recursive chain is not a supported integration route.

The inspected pack API supports DLL discovery with optional callbacks, and direct side-loading is now verified in the isolated game process. No adapter is needed solely to call `LoadLibrary`. An adapter would not fix incompatible game signatures. Any beta file remains a separately supplied, private dependency; it is not part of this project's redistributed payload.

### Installed 2021 API contract

The pack's older API was compared with [historical source revision `ff3b5b0b6060c7c2938fee6878fc3d8de434685f`](https://github.com/zealottormunds/ns4moddingapi/blob/ff3b5b0b6060c7c2938fee6878fc3d8de434685f/d3dcompiler_47_og/ccMain.cpp#L253). That scan uses immediate lowercase `.dll` files and pipe-separated title/description/author metadata. It calls `LoadLibraryA`, then looks up optional `InitializePlugin` and `GameLoop` exports. Missing callbacks are logged; the already loaded module is retained. Inspected binary branches agreed with optional-export handling. This contract, rather than the latest API's folder conventions, governs the current lab integration.

The old worker callback is `void (__stdcall *)(__int64 moduleBase)`, receiving `GetModuleHandle(NULL) + 0xC00`, and runs from a worker with `Sleep(10)`. It is not the simulation tick. Optional `InitializePlugin` takes an additional `std::vector<__int64>` value; the original diagnostics DLL exports only `GameLoop` and avoids passing that C++ standard-library object across compiler ABIs. Native120's attach-time initialization permits evaluating direct discovery without implementing either callback.

## Upstream source review

Exact revisions below were observed on 2026-10-15. Source age is separate from binary-release date.

| Project | Reviewed revision | Release observed | Relevance and limitation |
|---|---|---|---|
| [zealottormunds/ns4moddingapi](https://github.com/zealottormunds/ns4moddingapi/tree/564b99d64013fde93117baefebd985a6460366a9) | `564b99d64013fde93117baefebd985a6460366a9`, 2022-11-26 | [2.0](https://github.com/zealottormunds/ns4moddingapi/releases/tag/2.0), 2023-11-18 | CPK priority loading, plugins, message/EXE patches, character and partner expansion. Release notes describe Connections support as barebones. This latest source is not automatically the same as the pack's older API binary. |
| [zealottormunds/ns4charactermanager](https://github.com/zealottormunds/ns4charactermanager/tree/e316388d4d2f7d77681901ff3f45d14e62445cf4) | `e316388d4d2f7d77681901ff3f45d14e62445cf4`, 2020-08-18 | [v1.6](https://github.com/zealottormunds/ns4charactermanager/releases/tag/v1.6), asset named v1.62 | Existing roster, costume, PRM, SPCl Load and XFBIN editing routes. No current-install gameplay proof. |
| [TheLeonX/NSC-ModManager](https://github.com/TheLeonX/NSC-ModManager/tree/276116ebf5ba398a867793cb02ee6c33c0927645) | `276116ebf5ba398a867793cb02ee6c33c0927645`, 2026-08-30 | [2.1.2.1](https://github.com/TheLeonX/NSC-ModManager/releases/tag/2.1.2.1), 2026-08-30 | Includes Storm 4 paths and `.uns/.unse` formats as well as Connections. Targets .NET 10 Windows, references an x86 CpkMaker binary and sibling XFBIN_LIB project. The release points at an earlier commit than this branch head. |
| [TheLeonX/UltimateStormAPI](https://github.com/TheLeonX/UltimateStormAPI/tree/a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc) | `a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc`, 2026-08-30 | No GitHub release observed | Modern compiler proxy, native plugins and version-specific hooks. It is not an established source repository for HenDGS's FPS beta. |
| [SenjuWoo/naruto-storm4-modpack](https://github.com/SenjuWoo/naruto-storm4-modpack/tree/3192a6d2bc596b84cc4a14f4293e7c28f2ba5b2a) | `3192a6d2bc596b84cc4a14f4293e7c28f2ba5b2a`, 2026-10-07 | [v1.0.0](https://github.com/SenjuWoo/naruto-storm4-modpack/releases/tag/v1.0.0), 2026-08-29 | Existing source owner for this work, preserving the legacy archive release. The reviewed tree was documentation/attribution only; its existing CI did not test native code. |

[UltimateStormAPI's modern bootstrap](https://github.com/TheLeonX/UltimateStormAPI/blob/a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc/xinput9_1_0/xinput9_1_0.cpp#L15) also forwards compiler exports to the genuine `_o` module. [Its plugin scan](https://github.com/TheLeonX/UltimateStormAPI/blob/a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc/xinput9_1_0/UltimateStormAPI.cpp#L488) loads DLLs before checking optional initialization exports. This modern source reads `modState` but does not use it to suppress the initial DLL load; do not generalize an `info.txt` disable convention across loader versions.

[The modern API worker](https://github.com/TheLeonX/UltimateStormAPI/blob/a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc/xinput9_1_0/UltimateStormAPI.cpp#L614) polls `Update()` with `Sleep(1)`. It is not the simulation tick. [Its dynamics compensation](https://github.com/TheLeonX/UltimateStormAPI/blob/a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc/xinput9_1_0/Common.cpp#L46) interpolates empirically selected 30/60 FPS spring/inertia coefficients from ImGui's averaged FPS and clamps at its 60 FPS factors. It is not a comprehensive 120 FPS gameplay solution. [Storm 4 hooks](https://github.com/TheLeonX/UltimateStormAPI/blob/a2d0f2206f5e5ca81c87eaaecc8bc6f3cbe42bdc/xinput9_1_0/HookFunctions.cpp#L78) mix version-specific offsets and signatures; copying their numbers does not validate the installed executable.

## Content and permission boundaries

Nexus 672 requires author permission for modifications/assets and prohibits reupload elsewhere. No public HenDGS FPS source was located in this review. The three reviewed TheLeonX/character-manager projects contained no project license file; ns4moddingapi's bundled Lua copyright does not supply a project-wide license. Preserve the distinction between readable source and an explicit redistribution grant.

[Evolution Launcher, Nexus 508](https://www.nexusmods.com/narutoultimateninjastorm4/mods/508), was 1.11, updated 2026-10-11, when observed. Its listed terms prohibit modification, reupload and asset reuse. It remains a separately installed reference/test target, not an incorporated component.

Connections and Shinobi Striker assets remain player-local reference inputs. No character, animation, skeleton, shader, material, jutsu or stage conversion is yet proven by this snapshot. Shared naming or an importable file does not establish runtime behavior. No later avatar subsystem has been reverse engineered here.

## Current engineering result

[src/Diagnostics.cpp](src/Diagnostics.cpp) implements original read-only native diagnostics, version 0.1.0. Its optional worker callback checks bounded probe spans in the current process, reports probe errors/out-of-bounds spans separately, and records whether the separately named beta is loaded. The current fingerprint implementation hashes spans using Windows `CryptHashCertificate2`; the Python probe uses `hashlib.sha256`. It does not install hooks, alter game bytes, set FPS or prove gameplay.

[tools/probe_native120_runtime.py](tools/probe_native120_runtime.py) provides a separate read-only process probe with explicit process-image verification. [tools/build.py](tools/build.py) generates digest arrays from the public fingerprint data and builds the diagnostics DLL with Windows Crypt32. Tests exercise actual disposable Windows process boundaries as well as profile validation. The fingerprint-only native build also ran in the later side-load observation. Exact rebuild, test and DLL-hash receipts belong in `TEST_RESULTS.md`; each receipt applies to its recorded binary.

The next unresolved gameplay work is current-build timing support using verified equivalent hooks or a supported profile, followed by measured stock/pack Free Battle baselines and timing regressions. Unmatched guards must not be forced. Any diagnostics prerelease must remain labelled as diagnostics rather than a playable overhaul or 120 FPS fix. See [FEASIBILITY_MATRIX.md](FEASIBILITY_MATRIX.md), [ARCHITECTURE.md](ARCHITECTURE.md) and [ROADMAP.md](ROADMAP.md).
