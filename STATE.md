# State

Updated 2026-10-16. Original diagnostics component: 0.1.0. The requested ultimate overhaul, especially stable native120 Free Battle, remains unfinished.

Implemented: read-only native loader proof, SHA256-only core fingerprints, exact-PID/path runtime probe, tests and payload packaging. Existing pack loader and genuine compiler are retained. Both supplied beta profiles matched0/11 in an initialized copied game, including with the unchanged beta loaded separately. All22 spans were readable; no probe failures. See [TEST_RESULTS.md](TEST_RESULTS.md).

Last good gameplay source: original supplied pack and live install, preserved. This repository's diagnostic component changes no gameplay. The isolated experiment was closed, beta discovery disabled and the lab's original config restored. Live EXE, compiler DLLs, config and save hashes remained unchanged.

Next: verified timing support for the actual executable layout, measured restarted30/60/120 Free Battle baselines and the regression matrix in [BENCHMARKS.md](BENCHMARKS.md). Do not force the incompatible beta guards or build later content features on an unvalidated timing foundation.

Build/test/package commands are in [BUILD.md](BUILD.md). Logs and rollback are in [INSTALL.md](INSTALL.md). Private machine paths, backups and runtime receipts remain in the local owner folder outside public source. Source CI/release receipts must be verified on the exact pushed SHA; diagnostic publication cannot mark the gameplay goal complete.
