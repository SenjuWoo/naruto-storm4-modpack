# Build

Windows x64, Python 3.11+ and an installed MinGW g++ are required. The observed local compiler was GCC 15.2.0. No Python packages are needed. Resolve the actual interpreter when a Windows Store alias cannot run; do not install over personal tool configurations.

From the source root:

```text
python tools/build.py
python -m unittest discover -s tests -v
python tools/package.py
```

The build uses C++17, optimization, strict warnings, static compiler runtimes, Crypt32, stripped debug/symbol data and a zero PE timestamp. Its own DLL uses a fixed preferred image base with normal relocation/ASLR; this avoids MinGW's output-path-dependent default and is not a game offset. It validates shared fingerprints before generating `build/probes.h`. Output is `build/WooDiagnostics.dll`; compiler details are in `build/build.log`. The upload archive is `dist/WooDiagnostics-0.1.0.zip`.

Tests compile a small native boundary harness, load the real DLL into disposable processes, compare their mapped main `.text` before and after, exercise actual Windows read-only process access, and validate payload contents and deterministic ZIP metadata. These are not game/combat tests.

For a second build, use `python tools/build.py --output build-repeat` and compare DLL SHA256 values. A source-only clean rebuild must use the same compiler before claiming identical binary bytes. CI independently builds and runs the suite on Windows; it does not have the game or beta.

The native source is read-only compatibility diagnostics. No timing patch is implemented. Public configuration contains RVAs, lengths and SHA256 fingerprints, with no proprietary instruction spans. Private runtime evidence and compiled products are ignored by Git.
