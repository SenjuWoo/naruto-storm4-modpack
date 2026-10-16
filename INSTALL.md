# Install and rollback

Woo Diagnostics is an original read-only component for the inspected 2021 Storm4 ModdingAPI generation. It is not a 120 FPS fix, a standalone loader, or the complete legacy pack. See [TEST_RESULTS.md](TEST_RESULTS.md) for the exact scope.

Close every game instance before changing its mod folders. Prefer a full isolated copy of the existing installation. Extract the diagnostics archive's `moddingapi` directory into that copy; it adds only `mods/woo_diagnostics`. Keep both root compiler DLLs and all existing settings. No save installation is required.

The installed historical API recognizes `info.txt` with pipe-delimited metadata and immediate lowercase `.dll` files. It keeps modules without optional initialization callbacks. This component exports only the verified `GameLoop` callback and avoids the optional cross-compiler STL initialization ABI. Its callback is an API worker, not a simulation tick.

For rollback, close all game instances and remove only this component's folder from discovery. The historical API has no verified modern disable-line setting; renaming its `info.txt` to `info.txt.disabled` is a reversible local alternative.

## Logs

Default operation is quiet. Launch with `WOO_STORM4_DEBUG=1` to enable one bounded native report at `%LOCALAPPDATA%/SenjuWoo/Storm4Overhaul/logs/native-diagnostics.json`. It replaces the last report. Check the PID to avoid reading stale evidence. Probe failures and out-of-bounds entries are distinct from readable mismatches.

The separately run Python probe requests only query/read process access and requires an explicit PID plus exact image path:

```text
python tools/probe_native120_runtime.py --pid EXACT_PID --image ABSOLUTE_EXE_PATH --profiles config/native120-profiles.json --output EXISTING_OUTPUT_DIRECTORY/result.json
```

Exit 0 means a core profile candidate; 3 means no candidate; 1 means an inspection/report error. Even 11/11 does not prove later guards, applied patches or gameplay correctness. `--debug` enables capped logs at `%LOCALAPPDATA%/NarutoStorm4UltimateOverhaul/Logs/runtime-probe.log`. Run with the access needed to inspect the chosen process; the desktop game was not visible to the sandbox's process enumeration in the observed test.

## Beta experiment

The locally supplied beta is not included. Its 29 compiler exports forward to `_o`; do not rename it as the genuine original or overwrite the pack proxy. A separate module under its own historical-API mod folder was tested locally. Both embedded profiles failed every core span on the inspected game, so the experiment was disabled and the lab FPS setting restored. Do not promote this arrangement into normal play without a verified current-build timing implementation and Free Battle regressions.
