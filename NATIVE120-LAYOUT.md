# Native120 layout mapping for the installed executable

Status: static research record, 2026-11-07. This does not claim a working
Native120 profile or any gameplay result.

## Scope

The supplied Native120 `0.2.0-beta1` proxy embeds two core profiles and two
hook tables. Both core profiles report `0/11` against the installed Steam
executable (`NSUNS4.exe`, 24,686,592 bytes, SHA-256
`147e52a3e0d7382501a6777e158b37908e0b69d4e902079dc6e62dcae69bc257`).
This record answers a narrower question: are the timing functions absent, or
are they present at different addresses?

The method was read-only:

1. Extract each embedded core signature and hook body from the beta's public
   fingerprint tables.
2. Search the installed executable for exact matches.
3. Where exact matching failed, use several 16-byte anchors from the same
   body, score every candidate window by byte identity, and keep the best
   alignment. This tolerates shifted RIP-relative displacements without
   assuming a uniform offset.
4. Verify every selected live RVA lies inside the executable's `.text`
   section and read the expected length.

No game bytes are redistributed here. The live SHA-256 values identify the
observed spans only.

## Core profiles

Profile 0 is the base-game table; profile 1 is the EVO table. The installed
executable matches profile 0's first and second core spans exactly, and the
remaining spans at shifted addresses.

| # | Beta RVA | Installed RVA | Delta | Length | Installed span SHA-256 | Result |
|---:|---:|---:|---:|---:|---|---|
| 0 | `0xA0B50A` | `0xA0C29A` | `+0xD90` | 47 | `a01fa4ace514790e45217fb99372eb0d9f4d5699b8491023ec6b8f116f4f3ffc` | exact |
| 1 | `0x19D79A` | `0x19D95A` | `+0x1C0` | 32 | `9daac7fc7e98466c4e57def3ca53e28d578dbeb5c383fa90c447d0a83a14362f` | anchor-located; RIP displacements differ |
| 2 | `0x9E04F0` | `0x9E1320` | `+0xE30` | 24 | `b4342b6728cf083cf591bf7c405cbafb57bce4c24a981f96a2f5b79928852ac4` | exact |
| 3 | `0xA0B835` | `0xA0C5C5` | `+0xD90` | 32 | `6d25d1433285e912185ce297919dff05cf8801a990c64774123795bb9089b59e` | 30/32 bytes |
| 4 | `0x78F930` | `0x7915A4` | `+0x1C74` | 1015 | `2dc88f6ed46b9c4a25f31549d985f7938ba0e2e7a3146ec0a105e1f587e9ae29` | 972/1015 bytes |
| 5 | `0x78EE94` | `0x790B08` | `+0x1C74` | 302 | `e3b1a8ced8a0701fd3c574735e2ad5390c1adb29dd8c5fd4849c99e5a0a55264` | 288/302 bytes |
| 6 | `0x790FA0` | `0x792C58` | `+0x1CB8` | 42 | `40a351a55a4eea78e7912a88e84a23a709bf4b8247b2eef38a305565317a9d67` | 40/42 bytes |
| 7 | `0x5244E8` | `0x524D58` | `+0x870` | 20 | `7fa757415aaad3b1c487a88d77d88913dd3fcf72fe6f0d1cfab88d3c54200b23` | 18/20 bytes |
| 8 | `0x782566` | `0x7841DA` | `+0x1C74` | 128 | `dace78eba4d6cb0d26fca4f5102b610e28d9fa004430670a0d08372f71f9c36e` | 124/128 bytes |
| 9 | `0x7B16A5` | `0x7B3451` | `+0x1DAC` | 64 | `de76ea199b8b283d2bac01430705e7ba8ca4207110646f154d22bf9017fa8d99` | 62/64 bytes |
| 10 | `0x7B1BC5` | `0x7B3971` | `+0x1DAC` | 64 | `0da8504d7991774f1ff6d7869b1dac79345ab58aa52ff651845d4652a7fbc835` | 62/64 bytes |

The deltas range from `+0x114` to `+0x465C` across the whole mapping, so the
two profiles are not one uniformly relocated build. The `0xA0xxxx` cluster
moves by `+0xD90`; the `0x78xxxx` cluster moves by roughly `+0x1C74`; the
`0x7Bxxxx` pair moves by `+0x1DAC`.

## Hook functions

The beta's profile-0 hook table contains seven function bodies. All seven are
present in the installed executable with high byte identity:

| # | Beta RVA | Installed RVA | Delta | Body length | Byte identity | Installed body SHA-256 |
|---:|---:|---:|---:|---:|---:|---|
| 0 | `0x7B16A5` | `0x7B3451` | `+0x1DAC` | 124 | 90.3% | `97a7398553fe30c5612d7150e5cb1e7cfb10ca53e16a73bbf790c4e89529490e` |
| 1 | `0x7B1BC5` | `0x7B3971` | `+0x1DAC` | 116 | 91.4% | `4cac7bc27fe4c53aa9cbf6a8251923bb53be5e9e2846226d776fdf5efb1ebd20` |
| 2 | `0x319959` | `0x31DFB5` | `+0x465C` | 301 | 87.7% | `5c2e06bd003174b56c1d5aa93205253819156d97524b493c1f9c00d1ec1a117f` |
| 3 | `0x332BF8` | `0x332E7C` | `+0x284` | 124 | 88.7% | `0568f82fe0d87ffcf8576142e550ea9f12477a8a4ef104379559ce94fa2264e2` |
| 4 | `0x7A1BD8` | `0x7A38DC` | `+0x1D04` | 54 | 98.1% | `e78b973d4428e3ea8909a9da26aefdb8d83bfa535e8f5a72221b5f1e0c8e9f98` |
| 5 | `0x3564F1` | `0x356605` | `+0x114` | 212 | 90.1% | `f0953e33b15881fa4c392d65d4094cc50ac24aa9626b536dcb20bf31c05e8642` |
| 6 | `0x78FE03` | `0x791A77` | `+0x1C74` | 77 | 98.7% | `930f41e2ea7264a8bd66329a6312a85f712c082e1318b32c3bc1b40d67d2c2b7` |

## Profile-0 guard table

The activation function also checks a 15-entry guard table at beta VA
`0x180017258` (file offset `0x15A58`). Each entry is 24 bytes: RVA, expected-byte
pointer, length. The profile-0 entries are:

| # | Beta RVA | Length |
|---:|---:|---:|
| 0 | `0x799A20` | 16 |
| 1 | `0x79909C` | 16 |
| 2 | `0x79B184` | 16 |
| 3 | `0x218CF0` | 16 |
| 4 | `0xEF7AC0` | 4 |
| 5 | `0xF16CC8` | 4 |
| 6 | `0x12F9D58` | 4 |
| 7 | `0x12F9DB4` | 4 |
| 8 | `0xEEEAFC` | 4 |
| 9 | `0x47DF14` | 16 |
| 10 | `0x67AB88` | 16 |
| 11 | `0x7837C8` | 16 |
| 12 | `0xA9B9A0` | 16 |
| 13 | `0x357B84` | 16 |
| 14 | `0x78CF02` | 16 |

These are still the old build's RVAs. The 2026-11-08 attempt updated the core
and hook tables but not this guard table; the beta therefore still refused.
The next attempt must map these 15 entries to live RVAs and copy the live bytes
into each expected-byte slot. Do not bypass the guard branches.

## Why the beta still refuses

The beta does not search for these functions. It compares the installed image
against exact RVAs and expected bytes for each core profile, then requires the
hook bodies and later guard tables to agree before it writes anything. The
installed executable fails at the first exact comparison, so the patch path is
never entered. The match evidence above does not bypass that guard and does
not make the beta compatible.

## What a supported profile requires

A hash-only profile addition would be wrong: the beta's patch descriptors and
hardcoded hook addresses are bound to the older layouts, and the byte
differences include relative calls and state offsets.

The next engineering step is a translated profile:

1. Rebind the eleven core descriptors to the installed RVAs and the bytes
   recorded above.
2. Rebind the seven hook-table start/end addresses and body fingerprints.
3. Translate every patch descriptor and hardcoded hook address by the delta of
   its containing function, not by a global delta.
4. Re-check the later guard tables and the trampoline targets.
5. Test in an isolated copy, with `fps=120`, before any live-install change.
6. Measure stock/pack 30/60/120 Free Battle baselines and the regression matrix
   in [BENCHMARKS.md](BENCHMARKS.md).

Until that profile exists and passes an isolated run, the beta must remain
disabled outside deliberate compatibility experiments. No timing patch,
presented-FPS result, combat result or stability claim follows from this
mapping.
