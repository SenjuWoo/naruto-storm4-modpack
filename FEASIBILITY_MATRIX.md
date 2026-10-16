# Feasibility matrix

Snapshot: 0.1.0. Evidence basis: [RESEARCH.md](RESEARCH.md), upstream/static observations dated 2026-10-15, local runtime observations dated 2026-10-16, and the current source. This is a classification of engineering routes, not a list of completed gameplay features.

| Classification | Meaning |
|---|---|
| VERIFIED IMPLEMENTABLE | Implemented locally or a concrete mechanism is established by inspected source. In-game validation remains a separate requirement. |
| EXPERIMENTALLY PLAUSIBLE | A specific mechanism exists, but compatibility or behavior has not passed the required experiment. |
| REQUIRES RESEARCH | The required hook, format, dependency, behavior or design has not been established. |
| CURRENTLY BLOCKED | A named prerequisite prevents promotion or delivery now; the condition for clearing it is stated. |

## Priority 1: native 120+ FPS

| Feature | Classification | Evidence / next gate |
|---|---|---|
| Read-only on-disk and live core-signature diagnostics | VERIFIED IMPLEMENTABLE | Original 0.1.0 native diagnostics ran in the initialized copied game; an independent external probe completed all 22 reads. Public schema 2 stores SHA-256 fingerprints only. Current rebuild/test receipts remain separate. |
| Use the existing pack API to discover an additional DLL | VERIFIED IMPLEMENTABLE | Copied game intro and nine-entry mod list rendered, including Woo Diagnostics; the diagnostics module and both compiler-chain owners were observed loaded. This does not prove beta patching. |
| Side-load the separately supplied Native120 beta while retaining the pack proxy | VERIFIED IMPLEMENTABLE | Controlled copied-game process loaded exactly one unchanged `Native120.dll` alongside fingerprint-only diagnostics; pack proxy and genuine `_o` hashes remained unchanged. No adapter required. This proves loading only. |
| Advertise the supplied beta as supported on the inspected game | CURRENTLY BLOCKED | With the beta separately loaded, native and independent SHA-256-only probes still find 0/11 per profile; all 22 spans read without failure. Core-profile incompatibility/refusal remains. A verified current-build timing port/profile and full gameplay regressions are required. |
| Package the supplied beta inside a public overhaul release | CURRENTLY BLOCKED | Upstream permission does not allow reupload. Clear only with documented permission; a separately obtained private dependency remains possible. |
| Stable normal-speed 120 FPS Free Battle | REQUIRES RESEARCH | No battle/timing proof. Upstream explicitly leaves combat timing and collision/landing integration incomplete. |
| Movement, jumps, dash braking/steering and aerial camera corrections | EXPERIMENTALLY PLAUSIBLE | Upstream beta documents concrete corrections; this executable/pack combination has not validated them. |
| Input polling/buffering, repeated menu inputs and customization navigation | REQUIRES RESEARCH | Old upstream input patches are excluded from the current beta. Map actual input consumers and compare quick taps/held inputs. |
| Animation duration, startup/active/recovery/cancel windows, hitstop | REQUIRES RESEARCH | Requires game-thread timing and representative combat comparisons. Worker polling is not a simulation clock. |
| Collision, landing, hit registration, knockback, juggling and substitutions | REQUIRES RESEARCH | Requires live state/function mapping and measured regression coverage. |
| Match timer, UI, AI cadence, audio and cinematic synchronization | REQUIRES RESEARCH | No isolated timing evidence or completed corrections. |
| Decoupled 60 Hz simulation with 120+ Hz rendering/interpolation | REQUIRES RESEARCH | Render/simulation ownership and interpolatable state have not been established. This would be reported separately from native 120 Hz simulation. |
| Arbitrary 144/165/240 FPS, automatic fallback and frame pacing | REQUIRES RESEARCH | First establish the validated 120 FPS mode and mismatch behavior; do not extrapolate from a hardcoded 120 fix. |
| Optional frame generation | REQUIRES RESEARCH | No integration evaluated. It cannot satisfy the native-render/simulation milestone. |

## Priority 2: graphics and capture

| Feature | Classification | Evidence / next gate |
|---|---|---|
| Reversible graphics profiles using verified existing game settings | EXPERIMENTALLY PLAUSIBLE | Preserve the baseline config; inspect exact supported keys before generating presets. |
| Internal resolution, AA, anisotropy, texture filtering and LOD | REQUIRES RESEARCH | Establish which settings are engine-controlled and which require renderer hooks; measure image quality and cost. |
| Cel shading/outlines, shadows, AO, transparency and particle quality | REQUIRES RESEARCH | No shader/resource edits or visual comparisons implemented. Preserve anime readability. |
| Connections materials, outlines, textures and VFX | REQUIRES RESEARCH | Format and dependency conversion unproven. Use player-local assets only. |
| HDR/color management, frame pacing, shader stutter and effect pooling | REQUIRES RESEARCH | Requires renderer/API observation, color/frame captures and repeatable workloads. |
| Photo mode, replay capture and optional camera presets | EXPERIMENTALLY PLAUSIBLE | Modern API contains camera/render integration; local applicability, pause semantics and capture quality remain untested. |
| Ultrawide, aspect ratio, HUD/UI scaling | REQUIRES RESEARCH | Camera, screen-space transforms and UI constraints not mapped. |
| VANILLA+, ENHANCED ANIME, CINEMATIC and PERFORMANCE presets | REQUIRES RESEARCH | Names define later user choices; no evaluated preset payload exists. |

## Priority 3: combat

| Feature | Classification | Evidence / next gate |
|---|---|---|
| Preserve tilt attacks, chakra shuriken and the classic baseline | VERIFIED IMPLEMENTABLE | Preservation is the default scope: original mechanics are retained while experiments remain isolated. No gameplay fix is implied. |
| Edit existing PRM/moveset and roster data with established tools | EXPERIMENTALLY PLAUSIBLE | Existing managers expose editors; exact installed formats and battle dependencies need round-trip/runtime validation. |
| Secondary ninjutsu, configurable action mapping and expanded loadouts | REQUIRES RESEARCH | Map input, action dispatch, resource loading and character-specific dependencies without losing existing actions. |
| Combo branches/finishers, aerial jutsu, transitions and cancel options | REQUIRES RESEARCH | Requires animation/state/hitbox dependency mapping and timing proof. |
| Damage scaling, hitstun/juggle limits, counters, guard and recovery | REQUIRES RESEARCH | Requires measured balance rules and shared runtime hooks. |
| Awakening selection, leader/support interactions and team techniques | REQUIRES RESEARCH | Existing partner/condition infrastructure is a lead, not proof of new mechanics. |
| Tracking, targeting, movement differentiation and reliable hit detection | REQUIRES RESEARCH | No decision/collision hook or universal character rule established. |
| CLASSIC STORM 4, STORM 4 ENHANCED, CONNECTIONS HYBRID, CUSTOM SANDBOX rulesets | REQUIRES RESEARCH | Isolate changes first; presets must select verified behavior and preserve the classic profile. |

## Priorities 4-6: characters, backports and custom shinobi

| Feature | Classification | Evidence / next gate |
|---|---|---|
| Creator Stage A: one new roster slot without replacement | EXPERIMENTALLY PLAUSIBLE | Existing API/manager expansion mechanisms are concrete. Prove a new slot, complete resources and save safety in this pack. |
| Stage B: appearance presets and an existing selectable moveset | EXPERIMENTALLY PLAUSIBLE | Costume/roster editing routes exist. Rig, material and animation compatibility remain untested. |
| Stage C: controlled jutsu swaps from a verified catalog | REQUIRES RESEARCH | No compatibility catalog or mapped logic/VFX/hitbox dependency set exists. |
| Stage D: independent save/load presets, thumbnails and roster integration | REQUIRES RESEARCH | Define a versioned external schema only after Stage A works; no vanilla-save changes. |
| Stage E: full external or in-game creation interface | REQUIRES RESEARCH | UI integration and creator data model not implemented. |
| Stage F: original animations, morphs, awakenings and techniques | REQUIRES RESEARCH | Requires skeleton/controller, hitbox, render and executable behavior mapping. |
| Hair, face, eyes, skin, markings, clothing, accessories and weapons | REQUIRES RESEARCH | Modular mesh/material feasibility and per-part attachment rules not established. |
| Height/body proportions and rig-aware hitboxes | REQUIRES RESEARCH | No runtime morph/scale and collision equivalence proof. |
| Connections characters, costumes, jutsu, awakenings, animations, stages and QoL | REQUIRES RESEARCH | Prove one complete conversion with dependencies before building a pipeline. |
| Shinobi Striker asset conversion and retargeting | REQUIRES RESEARCH | Engine/format/rig differences require local inspection; no transfer demonstrated. |
| Striker-inspired specializations, elemental combinations, tools and mastery | REQUIRES RESEARCH | Design references only; no Striker system or gameplay code is portable by assumption. |
| Redistribute proprietary source-game assets | CURRENTLY BLOCKED | No distribution rights established. Keep extraction/conversion player-local and ship original tools only. |

## Priorities 7-9: AI, modes, compatibility and UX

| Feature | Classification | Evidence / next gate |
|---|---|---|
| AI aggression, spacing, support/substitution/awakening decisions and adaptation | REQUIRES RESEARCH | AI update/decision hooks and fair reaction/resource constraints not mapped. |
| Tournament, survival, boss rush, randomized teams and custom modifiers | REQUIRES RESEARCH | Mode ownership, round lifecycle and UI integration not mapped. |
| Advanced training, combo/damage analysis and mastery challenges | REQUIRES RESEARCH | Requires reliable combat-event observation before presentation. |
| Versioned source, debug toggle, bounded structured diagnostics and tests | VERIFIED IMPLEMENTABLE | Implemented in the original 0.1.0 diagnostics slice. This is tooling evidence, not a completed overhaul framework. |
| Unknown-version refusal and per-feature capability gates | EXPERIMENTALLY PLAUSIBLE | Probe validation exists; future patch installation must require every relevant live guard and a verified hook ABI. |
| Stock/experimental separation and rollback without touching saves | VERIFIED IMPLEMENTABLE | Isolated lab deployment is the chosen workflow. Restoration and game-load outcomes still require their own receipts. |
| General proxy chaining and multiple hook owners | REQUIRES RESEARCH | Beta `_o` recursion is rejected. Coexistence needs explicit load-order/ownership evidence; blind replacement is excluded. |
| Companion app/overlay for FPS, graphics, combat, input, camera, jutsu, AI and logs | REQUIRES RESEARCH | Diagnostics CLI is the current surface; the full requested configuration interface is not implemented. |
| Public online gameplay with modified rules/timing | CURRENTLY BLOCKED | No compatibility/desynchronization proof. Current target is isolated offline Free Battle. |
| Playable release candidate of the full overhaul | CURRENTLY BLOCKED | Native 120 FPS milestone, gameplay regressions, content features, packaging and release proof remain unfinished. |

Current conclusion: the diagnostics slice is concrete. The requested stable 120 FPS Free Battle prototype and later overhaul features remain unfinished. [ROADMAP.md](ROADMAP.md) names the next gates.
