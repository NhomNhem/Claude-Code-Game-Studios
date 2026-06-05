# Scene Manager — Review Log

## Review — 2026-05-26 — Verdict: MAJOR REVISION NEEDED
Scope signal: S
Specialists: game-designer, systems-designer, qa-lead, gameplay-programmer, creative-director
Blocking items: 8 | Recommended: 3
Summary: Foundational design problems: compile-blocking schema error (ZoneId lookup), pillar contradiction (LoadSceneMode.Single black flash vs P3 Snappy Sessions), incomplete state coverage (4 states unmapped), no cancellation architecture (race conditions + leaks), and 7/11 ACs untestable. All 8 blockers subsequently resolved in revision.
Prior verdict resolved: First review

### Revision summary (2026-05-26)
- Blocker 1: Added `zoneId` field to `ZoneSceneEntry`, changed array to `List<ZoneSceneEntry>`
- Blocker 2: Added `allowSceneActivation = false` + `SceneReadyToActivate`/`ActivateScene()` handshake (Rule 11)
- Blocker 3: Added queue depth of 1 (latest wins) for rapid transitions (Rule 5)
- Blocker 4: Added `CancellationToken` to `PreloadZoneAsync`, defined cancellation semantics
- Blocker 5: Added Rule 13 (explicit no-op for Loading/Paused/Defeat/Victory), registry table with Action column
- Blocker 6: Fixed Dependencies table: `TransitionTo(Menu)` consistently
- Blocker 7: Added Rule 12 (built-in CanvasGroup fade fallback when Loading/Transition absent)
- Blocker 8: Rewrote all 11 ACs + added 5 new ones (concrete, testable conditions)
