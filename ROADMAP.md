# Roadmap

Snapshot: 0.1.0. Stable native 120 FPS offline Free Battle is the first gameplay milestone. Current output is a diagnostics development slice, not a playable overhaul. Dates below describe evidence, not delivery estimates.

## Immediate gate: current-build support

The 2026-10-15 on-disk analysis found 0/11 matches in both embedded Native120 core profiles. On 2026-10-16, the copied game rendered its intro and nine-entry mod list, including Woo Diagnostics. A later initialized process loaded exactly one unchanged `Native120.dll` beside the SHA-256-only diagnostics build, retaining unchanged root-proxy and genuine-compiler hashes. Native and independent external probes both confirmed 0/11 per profile, all 22 spans readable and no out-of-bounds/probe failures. Controlled separate loading is complete; both core profiles remain incompatible with that observed image.

Some shared sequences occur elsewhere, so a guessed relocation remains unacceptable. The remaining gameplay work is a verified timing port/profile for the current build, measured stock/pack Free Battle baselines and regression proof. The public schema contains only SHA-256 fingerprints, and that native build ran in the side-load test. Rebuild/test/hash receipts remain recorded per binary. A lab request for `fps=120` is not a presented-FPS measurement.

| Step | Required evidence | Stop condition |
|---|---|---|
| Build and test original diagnostics | Compiler/test receipts, DLL identity, real disposable-host checks | Any read/bounds/image-identity or default-silence failure |
| Establish isolated stock/pack baseline | Copied-game launch/intro and pack-loader integration observed; measured stock/pack battle baselines still pending | Unexplained launch failure or loader chain |
| Verify native callback and live core probes | Completed on initialized copied game: native and external 0/11 per profile, all spans readable | No timing gameplay promotion while required guards mismatch |
| Evaluate controlled direct beta side-load/refusal | Completed: one unchanged beta loaded; compiler chain retained; native and independent external profiles remained incompatible | No promotion to timing support or gameplay while required guards mismatch |
| Resolve incompatibility at its cause | Correct supported binary profile or independently verified equivalent hooks | Guessing offsets, bypassing guards, or treating injection as patch proof |

If a game-load crash appears, preserve its evidence, restore the lab baseline and isolate the smallest change. Do not stack graphics, combat or content experiments onto an unresolved loader/timing failure.

## Requested milestones

| Milestone | Current status | Acceptance evidence |
|---|---|---|
| 1. Reconnaissance, backups, baseline and native plugin proof | PARTIAL | Inventory/source/static analysis and original diagnostics implemented; copied-game intro/mod list, native callback and controlled beta side-load observed; independent fingerprint probe agreed. Measured battle baselines and exact build/test receipts remain separate gates in `TEST_RESULTS.md`. |
| 2. Stable native 120 FPS Free Battle | NOT COMPLETE | Comparable restarted 30/60/120 sessions; normal-speed movement, jump, combat, input, camera, timer and round lifecycle; representative regressions; presented-frame and frame-time proof. |
| 3. Graphics and performance improvements | NOT STARTED | One reversible enhancement at a time, paired captures and measured cost, anime fidelity preserved, evaluated presets. |
| 4. Enhanced combat framework | NOT STARTED | Classic baseline retained, selectable isolated ruleset and one complete new mechanic with dependency/timing/balance proof. |
| 5. Connections conversion | NOT STARTED | One local character, animation or jutsu conversion with all required dependencies and complete battle behavior verified; repeatable conversion steps. |
| 6. Custom-shinobi prototype | NOT STARTED | New roster slot, configurable appearance and compatible moves; persistence across sessions; no replaced vanilla character or damaged save. |
| 7. Expanded creation, AI and modes | NOT STARTED | Creator stages C-F, fair measured AI behavior and individual mode/regression proof after core stability. |
| 8. Compatibility and release candidate | NOT COMPLETE | Clean package/install/rollback, exact source SHA with required CI/security results, allowed payload, public release and independently verified download bytes. |

## Order within the 120 FPS milestone

1. Separate present rate from simulation cadence and identify the real game-thread update boundaries.
2. Prove movement distance, quick/held jump trajectory, dash acceleration/release/braking, steering and aerial camera continuity against the reference mode.
3. Prove animation and action durations, quick/held input delivery, hitstop, startup/active/recovery/cancel windows and resource/timer behavior.
4. Prove ground/air combos, contact/landing, hit registration, knockback/juggle, guard/counter/substitution, support/leader switching and awakenings.
5. Prove cinematic/audio/UI/AI timing and round transitions, then broaden characters/forms/stages and sustained-session coverage.
6. Decide from measured architecture whether higher targets or render interpolation are viable. Label a 60 Hz simulation plus 120 Hz renderer explicitly if that is the result.

No frame-generation or FPS-counter-only result substitutes for these gates. [BENCHMARKS.md](BENCHMARKS.md) defines the comparison record.

## Handoff

Read the owner's `STATE.md`, current source diff and `TEST_RESULTS.md` before continuing. Reuse the pinned 2026-10-15 research when inputs are unchanged. Refresh upstream only when a version, hash, permission or documented behavior changes. Keep private machine paths, saves and raw local reports out of public source/release payloads.

Controlled beta side-load/refusal evidence is complete. The next unresolved work is current-build timing support, measured Free Battle baselines and gameplay regressions. Packaging an original diagnostics prerelease can preserve this proven slice, but does not complete the 120 FPS goal. Implementing later avatar or graphics scaffolding before timing support would not advance the first gameplay milestone.
