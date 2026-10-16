# Test results

Observed 2026-10-16. Component: original read-only Woo Diagnostics 0.1.0. Stable native120 Free Battle and the requested overhaul are unfinished.

## Implementation checks

- Strict MinGW GCC15.2.0 C++17 build passed with warnings treated as errors.
- Eleven local tests passed in the final combined suite: eight process-probe tests, one real native loader/mapped-text test, one native hash/bounds/read-failure test, and one deterministic payload test.
- Quiet and debug child processes each preserved all3,628 mapped mainEXE .text bytes across DLL load and two callback calls. This does not prove every memory region or gameplay behavior unchanged.
- Native guard harness used an independent Python SHA256 oracle to prove matching, readable mismatch, out-of-bounds refusal and inaccessible-page failure.
- Shared config schema2 contains22 SHA256 fingerprints and no game instruction bytes. Runtime reports contain fingerprints rather than raw instruction spans.
- Archive test enforces exactly this component's five runtime files and deterministic ZIP bytes; it excludes beta/game files and development scripts.

Native source SHA256: C2929B0AD96EDB57744B173E5003139D2F4888CB3E7705E5FEFA321685286730

Runtime-tested native DLL SHA256: 88B9B815DE9EEF74B2C143B0AF43D85F30234ADA243D9F96AE3E20D076A464B9

Local diagnostic ZIP SHA256: EB9A6EE65B6129008A8A75B8E8D8BFD24F883668D04806EA9A134A3FE880310F

Two cross-directory native builds were byte-identical after fixing MinGW's output-path-dependent preferred image base and stripping compiler debug/symbol data. Timestamp-only normalization was insufficient. The final exact 53,248-byte DLL was loaded again in the restored copied game: all22 spans readable,0/11 per profile,no errors,beta absent. The independent fingerprint-only probe agreed. The save hash remained unchanged afterward.

## Actual copied-game evidence

The full isolated copy completed:5,959 files, zero failed/mismatched copies. Important inputs matched their installed originals. The source installation was already modded, so this is a pack baseline, not a claimed pristine Steam baseline.

The copied game rendered its intro and historical API mod list with Woo Diagnostics. Module inspection verified the root API, genuine compiler and original diagnostics loaded from the lab. The native GameLoop callback executed and an independent explicit-PID process probe read the same core spans.

A second run requested fps120 only in the lab config and loaded exactly one unchanged beta as a separately named Native120.dll. The root API and genuine compiler retained their original hashes. Native and external checks both found0/11 matches in each beta core profile. All22 spans were readable; no out-of-image or probe errors. The external probe returned incompatible/exit3 and the native report recorded beta-module presence separately from profile acceptance.

Inspected game EXE SHA256:147e52a3e0d7382501a6777e158b37908e0b69d4e902079dc6e62dcae69bc257.

Root API SHA256:5e486da44a327863b9cbbd2fc88f0df76b07d6577bea2dd08f14762b0c521afb.

Genuine compiler SHA256:e994847e01a6f1e4cbdc5a864616ac262f67ee4f14db194984661a8d927ab7f4.

Locally supplied beta SHA256:dfb9706e17892cd0d9cad7fb4378e1e15981e8245361711f9b7ab51b6e181651.

This proves separate module loading and incompatible core profiles. It does not establish120 FPS patch activation, stable FPS, accurate simulation or combat correctness. Later beta guards and complete hook compatibility are separate unpassed gates.

## Recovery and limitations

Sandbox launches exited before a usable game window; desktop-access launch succeeded. Sandbox process enumeration could not see that desktop process. Initial native screenshots sometimes captured an unfocused/transitional frame; an observed rendered intro/mod list is the visual evidence. No public screenshots are included because the local desktop overlay contains unrelated identifiers.

Automatic review rejected one side-load launch because its guard checked only one stale PID. A fresh all-process inspection found no running game; the retry guarded all Storm4 processes before writes and launch. No rejected command ran.

After testing, the exact owned lab process was stopped, beta discovery disabled and the lab config restored. The live save, live EXE, both live compiler DLLs and live config hashes remained unchanged. Backups and private raw receipts remain local and ignored by Git.

## Unpassed gameplay gates

No Free Battle round, movement/jump/dash parity, combo/contact/landing, timer/input/camera, AI/audio/cinematic or sustained-session regression is claimed. No FPS,1%low,latency or frame-time measurement is claimed. [BENCHMARKS.md](BENCHMARKS.md) records pending metrics. Current-build timing support and those regressions are the next work, before graphics/combat/content expansion.

CI independently builds/tests this source without the games. Exact source-SHA checks and downloaded artifact hashes belong to the release receipt; CI success cannot promote these diagnostics into a gameplay fix.
