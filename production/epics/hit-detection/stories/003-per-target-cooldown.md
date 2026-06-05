# Story 003: Per-Target Hit Cooldown

- **Epic**: Hit Detection
- **System**: Hit Detection — Cooldown
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 2h
- **Status**: Complete
- **Last Updated**: 2026-06-04

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-hitdetect-002` | Same enemy hit twice within 0.3s → only one HitEvent | ✅ ADR-002 |

## ADR Guidance

**ADR-002 (Event Bus Contract):**
- Cooldown is a Hit Detection internal concern — Event Bus subscribers receive a single HitEvent and should not need to deduplicate
- Cooldown window configured via `HitCooldownConfig` ScriptableObject (default: 0.3s)

## Description

Prevents a single hitbox from generating multiple HitEvents against the same hurtbox within a configurable cooldown window. Uses a Dictionary keyed by hurtbox instance to track the last hit time per target, with periodic cleanup of stale entries to prevent unbounded memory growth.

## Design

- `HitCooldownConfig` ScriptableObject with single field: `float cooldownSeconds = 0.3f`
- `HitCooldownTracker` (component, injected by VContainer):
  - `Dictionary<IHurtbox, float> _lastHitTime` — maps hurtbox → last HitEvent timestamp
  - `bool CanHit(IHurtbox target, float now)`: returns false if `now - _lastHitTime[target] < cooldownSeconds`
  - `void RecordHit(IHurtbox target, float now)`: updates `_lastHitTime[target] = now`
- HitResolver (Story 002) calls `CanHit` before publishing, `RecordHit` after
- Stale entry cleanup: periodically (every 100 checks or every 10s) scan and remove entries where `now - timestamp > cooldownSeconds * 2`
- Thread-safe not required — all Unity main-thread calls

## Acceptance Criteria

1. First hit on target within 0.3s → HitEvent published
2. Second hit on same target within 0.3s → no HitEvent published
3. Hit after 0.3s cooldown expires → HitEvent published again
4. Cooldown configurable via HitCooldownConfig ScriptableObject (default 0.3f)
5. Stale entries are cleaned up periodically (no memory leak from one-shot enemies)
6. Different targets have independent cooldown timers
7. No exception when tracker has no entry for a target (first hit)

## QA Test Cases

- **AC1 (First hit)**: First hit on target within 0.3s. Verify HitEvent published.
- **AC2 (Second hit within)**: Second hit on same target within 0.3s. Verify no HitEvent published.
- **AC3 (Cooldown expired)**: Hit after 0.3s cooldown expires. Verify HitEvent published.
- **AC4 (Configurable)**: Change HitCooldownConfig.cooldownSeconds to 0.5s. Verify new window applies.
- **AC5 (Stale cleanup)**: Add entries, advance time beyond cooldown*2. Verify entries removed from tracker.
- **AC6 (Independent targets)**: Hit target A twice within 0.3s (one event). Hit target B (event). Verify target B not blocked by A's cooldown.
- **AC7 (First hit no entry)**: CanHit with no prior entry. Verify returns true.

**Edge cases**: Multiple RecordHit calls in same frame, destroyed hurtbox in tracker.

## Test Evidence Path

- `tests/Foundation/HitDetection/TestHitCooldown.cs`
- Unit tests: time-based with manual Time.time mocking, verify CanHit/RecordHit cycle
- Integration: rapid-fire trigger events within cooldown → single HitEvent

## Dependencies

- **Depends on**: Story 002 (Hit Event Dispatch)
- **Unlocks**: None

## Risks

- `Time.time` dependency makes tests fragile — use `ITimeService` abstraction or `Time.timeAsDouble` with testable wrapper
- Dictionary memory: cleared entries from destroyed hurtboxes must be removed — guard with null check in cleanup pass

## Completion Notes
**Completed**: 2026-06-04
**Criteria**: 7/7 passing
**Deviations**: Advisory — test path differs from spec (actual: `Assets/_TinyRift/Tests/EditMode/Combat/TestHitCooldown.cs`); HitCooldownTracker is plain C# class (not VContainer component) to match existing patterns
**Test Evidence**: Logic: `Assets/_TinyRift/Tests/EditMode/Combat/TestHitCooldown.cs` (20 tests)
**Code Review**: Complete — APPROVED WITH SUGGESTIONS
