# Benchmarks

Snapshot: 0.1.0. No gameplay/performance result is established by this document. Missing measurements are **PENDING**, never zero. Compiler tests, DLL loading and signature matches do not measure frame pacing or combat correctness.

## Current results

| Metric | 30 FPS session | 60 FPS session | 120 FPS session |
|---|---|---|---|
| Average presented FPS | PENDING | PENDING | PENDING |
| 1% low FPS and calculation method | PENDING | PENDING | PENDING |
| Frame-time median/p95/p99 and variance | PENDING | PENDING | PENDING |
| Native presents versus generated/interpolated frames | PENDING | PENDING | PENDING |
| Input-to-action latency and measurement resolution | PENDING | PENDING | PENDING |
| Movement distance over fixed real time | PENDING | PENDING | PENDING |
| Quick-tap/held jump height, duration and landing | PENDING | PENDING | PENDING |
| Dash acceleration, braking, steering and release duration | PENDING | PENDING | PENDING |
| Animation/action duration in milliseconds | PENDING | PENDING | PENDING |
| Startup/active/recovery/cancel and input-buffer windows | PENDING | PENDING | PENDING |
| Match timer error against elapsed real time | PENDING | PENDING | PENDING |
| Hits registered / attempts and combo completion | PENDING | PENDING | PENDING |
| Collision/knockback/juggle and landing consistency | PENDING | PENDING | PENDING |
| UI/camera/cinematic/audio/AI timing | PENDING | PENDING | PENDING |
| Crashes, softlocks and round-transition failures / exposure | PENDING | PENDING | PENDING |

Theoretical per-frame budgets are 33.333 ms at 30 FPS, 16.667 ms at 60 FPS and 8.333 ms at 120 FPS. These are `1000 / target FPS`, not observed frame times.

The compatibility record is separate from every gameplay/performance metric above:

| Compatibility observation | Result | Scope |
|---|---|---|
| On-disk executable, 2026-10-15 | 0/11 matches for each embedded beta profile | Static image only |
| Native diagnostics in initialized copied game, 2026-10-16 | Matches `[0,0]`; readable `[11,11]`; out-of-bounds/probe failures `[0,0]` | Original native diagnostics/callback ran; core profiles incompatible with this observed image |
| Independent external live probe, 2026-10-16 | 22 successful reads; 0/11 matches for each profile | Confirms live mismatch independently |
| Copied-game presentation | Intro rendered; nine-entry mod list included Woo Diagnostics | Startup presentation only, not measured FPS or a battle |
| Native120 in the initial diagnostics observation | Not staged/loaded | Initial receipt only |
| Later controlled beta side-load, 2026-10-16 | Exactly one unchanged `Native120.dll`, plus fingerprint-only diagnostics, loaded; root API and genuine compiler hashes unchanged | Separate loading verified without adapter/proxy replacement |
| Native and independent probes after beta side-load | 0/11 per profile; all 22 spans readable; no out-of-bounds/probe failures; external status `ok`, `incompatible`, exit 3 | Core-profile incompatibility/refusal remains; no timing-patch or battle proof |
| Lab FPS configuration in side-load experiment | `fps=120` requested | Configuration only; presented FPS unmeasured |

Current public schema 2 stores only span fingerprints. Native comparison uses `CryptHashCertificate2`; Python comparison uses `hashlib.sha256`; both ran in the later side-load experiment. Exact rebuild/test/hash receipts remain tied to the recorded binary in `TEST_RESULTS.md`. Full timing support for the current build, measured Free Battle baselines and gameplay regressions remain pending.

## Reproducible comparison

Use the same isolated executable, stage, character/form pair, roster, graphics settings, display mode, input device and overlay set. Record exact file hashes and module identities. Preserve a stock baseline and a pack baseline separately; a pre-existing pack change must not be attributed to the FPS experiment.

For each target, set the game's own FPS setting and restart. Do not create the 30/60 reference by externally limiting a 120-configured session. Record VSync, VRR, driver caps, frame generation and display refresh; distinguish their configuration from measured presentation behavior. Begin at the intended 1440p quality baseline and keep it fixed during timing comparisons.

After a repeatable warm-up, capture at least three repetitions of the same workload and record capture duration, exclusions and tool/version. Extend capture when the workload is variable or failures are rare. Repetitions characterize variability; they are not evidence of an unmeasured long-session failure rate.

## Small behavior suite

| Workload | Observe |
|---|---|
| Fixed-time straight movement, turns and curved movement | Distance, acceleration and steering geometry |
| Quick tap and held jump, repeated from rest and motion | Input delivery, launch time, apex, flight time, landing/contact |
| Repeated chakra dash, direction change and release | Acceleration, travel, braking, redirection and recovery |
| Full ground and air combo, repeated at fixed spacing | Hit count, damage, duration, missed finisher, knockback and juggle |
| Guard, counter, substitution and cancel sequences | Response, resource cost, invulnerability/stun and allowed timing |
| Support use, leader switching and awakening | Resource cadence, state transitions, effects and interruption behavior |
| Timed round, round end and rematch | Timer accuracy, resets, state cleanup and softlocks |
| Ultimate/cinematic sequence, menu/customization navigation | Camera continuity, audio sync, UI cadence, lost or repeated inputs |

Record character/form, opponent, stage, initial spacing/state, exact input sequence and attempts. A general timing fix requires representative characters, movement types, transformations, partner/support behavior and collision cases. Include retained upstream reports as explicit regression cases rather than assuming they are fixed.

## Measurement rules

Use a presentation/frame-time capture that identifies the actual process and reports real presents. Preserve raw capture privately and publish sanitized summaries. A visible FPS counter alone is insufficient. If a selected tool cannot distinguish generated frames, mark that distinction unmeasured.

Measure animation, movement, timers and combat against elapsed real time, not only frame counts. Report observed frames and milliseconds together when useful. Record video/capture rate, timestamp source and uncertainty. Input-to-action latency needs an observable input event and response endpoint; sampling alone cannot prove sub-sample precision.

Report hit and combo outcomes as successes/attempts. Report failures with duration, rounds and scenario exposure. An unobserved crash is not a zero crash rate without the exposure denominator. Compute 1% lows and variance from the retained frame-time samples using one named method across every mode.

Before comparing behavior, establish reference repeatability and measurement resolution. Declare a tolerance from that evidence, then report absolute differences and spread. Do not invent tolerances after seeing an unfavorable result. Preserve intended combat timing; smoother animation cannot compensate for changed cancel windows or hit behavior.

## Pass and failure gates

The Free Battle prototype passes only after actual 120 FPS presentation, normal gameplay speed, stable frame pacing, consistent combat behavior, relevant regression scenarios and repeatable session/round lifecycle have evidence. A match against 11 core signatures is a prerequisite candidate check, not that verdict. Record all later patch guards separately.

Any acceleration, delayed/duplicate input, altered match duration, missed hit, unstable landing/contact, altered combat window, crash or softlock is an unresolved failure. Preserve its smallest reproducible case, roll back the experiment in the lab and fix it before adding another feature.

Graphics comparisons come later: pair matching-frame captures, preserve color/display settings, compare outlines, transparency, shadows and VFX readability, and record frame-time/memory cost. No graphics preset or native-120 claim is ready on the basis of the current diagnostics slice.
