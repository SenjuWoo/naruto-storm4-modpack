# Architecture

Snapshot: 0.1.0. The implemented slice is read-only compatibility diagnostics. It neither changes the game's timing nor implements a new combat system.

## Existing pieces first

Keep the supplied pack API as the loader owner and keep the genuine compiler available under its expected name. Its DLL discovery already supports an additional module with optional callbacks, so a new adapter solely for `LoadLibrary` is unnecessary. The inspected 2021 pack loader and the modern UltimateStormAPI source are separate versions; do not replace one with the other or assume their callback details are identical.

The separately supplied Native120 beta is an external experiment. Its patch routine runs during module attachment; loading it successfully is not evidence that its compatibility guards accepted the game. Direct separate loading has now been verified, while both core profiles remain incompatible with the observed initialized game. The original diagnostics module is independent and does not call the beta's patch routine.

```text
isolated Storm 4 process
  |
  +-- existing pack compiler proxy / mod API
  |     +-- genuine compiler, preserved under the expected original name
  |     +-- discovered mod DLLs
  |           +-- WooDiagnostics.dll: optional read-only worker callback
  |           +-- Native120.dll: separately supplied beta, optional lab experiment
  |
  +-- external read-only process probe
        +-- explicit PID and expected image identity
        +-- same pinned core-probe data
        +-- local JSON report
```

On 2026-10-16, the copied game rendered its intro and API mod list, loaded Woo Diagnostics and retained the root API plus genuine compiler. In a subsequent initialized process, the diagram's separate beta branch was verified: exactly one unchanged `Native120.dll` and the SHA-256-only diagnostics DLL loaded without changing either compiler-chain hash. Native and independent external probes both found 0/11 per profile, all 22 spans readable and no out-of-bounds/probe failures. Module discovery is proven for this setup; compatible timing patches and gameplay correctness are not.

## Implemented source boundaries

| File | Responsibility |
|---|---|
| [config/native120-profiles.json](config/native120-profiles.json) | Schema 2 pins the beta identity and two ordered sets of 11 core-probe RVAs, lengths and `expected_sha256` values. Contains no game instruction bytes and is not an offset patch. |
| [tools/build.py](tools/build.py) | Validates probe shape/lengths/digests, generates fingerprint arrays in `probes.h`, compiles the original native DLL with MinGW and Crypt32, and records compiler output. |
| [src/Diagnostics.cpp](src/Diagnostics.cpp) | Exposes the worker callback, reads bounded spans, hashes with `CryptHashCertificate2`, records match/read/out-of-bounds/probe-failure counts and beta-module presence. Does not install hooks or write game memory. |
| [tools/probe_native120_runtime.py](tools/probe_native120_runtime.py) | Opens an explicitly identified process with query/read permissions, verifies its executable identity, validates profiles, compares live-span SHA-256 using `hashlib`, and writes a report. |
| [tests/test_native_proof.py](tests/test_native_proof.py) | Exercises the actual compiled DLL in a disposable Windows host, including debug-off silence and debug-on reporting. This is not a game host. |
| [tests/test_probe_native120_runtime.py](tests/test_probe_native120_runtime.py) | Tests all-probe acceptance, mismatch, bounds, malformed input, explicit image checks and actual read-only process access. |

The inspected 2021 API calls `GameLoop(__int64 moduleBase)` from a worker with `Sleep(10)` and passes the main image base plus `0xC00`. It accepts a module without `InitializePlugin`; the original DLL exports only `GameLoop`, avoiding the optional initialization export's cross-compiler `std::vector` argument. See the [pinned historical scan](https://github.com/zealottormunds/ns4moddingapi/blob/ff3b5b0b6060c7c2938fee6878fc3d8de434685f/d3dcompiler_47_og/ccMain.cpp#L253).

This callback is worker polling, not a simulation tick. Do not perform future deterministic gameplay integration from its cadence. A timing feature needs a separately verified game-thread hook and function ABI.

## Diagnostics behavior

The native module's default is quiet. Set `WOO_STORM4_DEBUG=1` before process launch to enable its one-time report. Its standard per-user location is `%LOCALAPPDATA%/SenjuWoo/Storm4Overhaul/logs/native-diagnostics.json`. The file replaces the last report rather than growing per frame. Process identity fields in local reports are diagnostic evidence, not public documentation.

Each profile accounts separately for matching, readable-but-different, out-of-image and failed probes, including read/hash failures. All 11 exact span fingerprints must match before reporting a core-profile candidate. Candidate status does not validate later beta patch guards, hook order or game behavior. The report always marks gameplay validation false. The fingerprint build ran in the later side-load process; exact hashes and tests belong in `TEST_RESULTS.md` and remain tied to their recorded binary.

The external probe takes an explicit process image and PID instead of choosing an arbitrary similarly named process. It does not request process memory-write or memory-operation rights. Its optional debug logs remain separate from game saves/configuration. Exact invocation and executed outcomes belong in `BUILD.md`, `INSTALL.md` and `TEST_RESULTS.md`.

## Loader and ownership rules

1. One root compiler proxy owns the entry point. Never blindly overwrite the pack proxy.
2. `_o` remains the genuine compiler. The beta's 29 exports forward there; placing the beta at `_o` creates a recursive export chain.
3. Side-load a separately named beta only in an isolated offline lab and only with a recorded module inventory. The controlled test observed exactly one copy. Keep this unsupported beta disabled outside deliberate experiments; do not load a second copy under another name.
4. Remove a DLL from discovery to disable it unless that exact loader's disable semantics have been verified. Modern UltimateStormAPI reads a state string without suppressing its initial load.
5. Preserve installed files, user configuration and saves. Lab copies and project-owned output carry experiments; no dependency installer should replace live tools or loaders.
6. Ship original source/tools and permitted payload only. Beta binaries and source-game assets stay outside redistributed artifacts.

## Future extension points

Add a feature only after its smallest vertical slice has a verified trigger, signature/ABI, state ownership and rollback. A timing feature must declare whether it changes simulation frequency or only rendering/interpolation. A combat change must declare the ruleset and preserve the classic baseline. A character change must name its complete resource, skeleton, animation, effect and gameplay dependencies.

Separate feature toggles become useful when there is an implemented feature to select. A gameplay configuration system, launcher/overlay, conversion pipeline, preset catalog and AI framework are future work, not additional scaffolding in 0.1.0. Controlled beta side-loading is complete. The next unresolved boundary is a verified current-build timing implementation, measured Free Battle baselines and gameplay regressions. A diagnostics prerelease must not be presented as that gameplay milestone.
