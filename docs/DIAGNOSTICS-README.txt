Woo Diagnostics 0.1.0 - read-only native compatibility diagnostics

This component does not unlock FPS, change combat, or include Native120.
Requires Windows x64 and the separately installed 2021 Storm4 ModdingAPI.
Its old loader accepts an optional GameLoop callback without InitializePlugin.
Do not replace either root compiler DLL to install this component.

With the game closed, extract the moddingapi folder into an isolated copy of
your game. The archive contains only this component's own mod folder.
For rollback, close the game and remove only woo_diagnostics from discovery.

Logging is quiet by default. Set WOO_STORM4_DEBUG=1 in the game's environment
before launching to write one report to:
%LOCALAPPDATA%\SenjuWoo\Storm4Overhaul\logs\native-diagnostics.json
The last report is replaced. Match, readable, out-of-image and failure counts
are separate. Eleven matches in a profile are only a core candidate, never
proof of applied patches or correct gameplay.

The inspected game build matched neither supplied beta profile. Keep that beta
out of normal play until current-build support and Free Battle regressions pass.
The matching repository includes an explicit-PID read-only Python probe.
Source: https://github.com/SenjuWoo/naruto-storm4-modpack
