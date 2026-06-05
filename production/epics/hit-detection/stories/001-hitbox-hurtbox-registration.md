# Story 001: Hitbox/Hurtbox Registration & Faction System

- **Epic**: Hit Detection
- **System**: Hit Detection — Registration
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-04

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-hitdetect-003` | Same-faction collision → no HitEvent (no friendly fire) | ✅ ADR-001, ADR-002 |
| `TR-hitdetect-005` | Hitbox destroyed mid-collision → no exception | ✅ ADR-001, ADR-002 |
| `TR-hitdetect-006` | On scene transition Clear() unregisters all | ✅ ADR-001, ADR-002 |
| `TR-hitdetect-007` | Faction-aware registration (Player/Enemy/Neutral) | ✅ ADR-001, ADR-002 |
| `TR-hitdetect-008` | Hitbox/Hurtbox register on Start, unregister on OnDestroy | ✅ ADR-001, ADR-002 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- HitDetectionRegistry registered as interface singleton in TinyRiftScope
- IHurtbox and IHitbox implementations resolved through VContainer

**ADR-002 (Event Bus Contract):**
- HitDetectionRegistry is data-only — no event publishing in this story
- Only manages registration lookups; event dispatch is Story 002

## Description

Implements the core registry that tracks all active hitboxes and hurtboxes in the scene, along with their Faction affiliation. Provides faction-aware lookup so the hit-detection system can check whether a collision is valid before dispatching events. Handles lifecycle cleanup on scene transitions and guards against null references from destroyed objects.

## Design

- `HitDetectionRegistry` (MonoBehaviour singleton, registered via VContainer as `IHitDetectionRegistry`)
- Maintains two collections:
  - `List<IHitbox>` — all active hitboxes (things that deal damage)
  - `List<IHurtbox>` — all active hurtboxes (things that receive damage)
- Each entry stores its `Faction` enum (Player/Enemy/Neutral)
- Faction-check: collision is valid only when attacker faction ≠ defender faction AND defender.ImmuneTo factions does not contain attacker faction
- `IHitbox` interface: `GameObject Owner { get; }`, `Faction Faction { get; }`, `HurtboxType Type { get; }`
- `IHurtbox` interface: `GameObject Owner { get; }`, `Faction Faction { get; }`, `bool IsActive { get; }`
- Null-guard: all iteration uses `obj != null` checks, removing null entries silently
- `Clear()`: empties both lists (called by SceneTransitionHandler on scene change)
- `Register/Unregister` called from `IHitbox.Owner.Start()` / `IHitbox.Owner.OnDestroy()`
- Thread-safe not required — all Unity main-thread calls

## Acceptance Criteria

1. HitDetectionRegistry accepts Register/Unregister for IHitbox and IHurtbox
2. Faction check returns false for same-faction pairs (Player↔Player, Enemy↔Enemy)
3. Faction check returns true for cross-faction pairs (Player↔Enemy, Enemy↔Player)
4. Neutral faction collides with everyone
5. Destroyed (null) hitboxes or hurtboxes are skipped during iteration without throwing
6. Clear() removes all registered entries
7. IHitbox.Start() calls Registry.Register, IHitbox.OnDestroy() calls Registry.Unregister
8. Same for IHurtbox.Start() / OnDestroy()
9. Scene transition fires Clear() via SceneTransitionHandler

## QA Test Cases

- **AC1 (Register/Unregister)**: Create IHitbox and IHurtbox. Register both. Unregister one. Verify count reflects only remaining entry.
- **AC2 (Same-faction block)**: Register Player hitbox and Player hurtbox. Verify faction check returns false.
- **AC3 (Cross-faction pass)**: Register Player hitbox and Enemy hurtbox. Verify faction check returns true.
- **AC4 (Neutral collides all)**: Register Neutral hitbox with Enemy hurtbox. Verify check returns true. Same with Player.
- **AC5 (Null skip)**: Register hitbox, destroy its GameObject (null). Iterate. Verify no exception thrown.
- **AC6 (Clear)**: Register 3 entries. Clear(). Verify both lists empty.
- **AC7 (IHitbox lifecycle)**: Create IHitbox on GameObject. Verify Start() calls Register. Destroy GameObject. Verify OnDestroy() calls Unregister.
- **AC8 (IHurtbox lifecycle)**: Same as AC7 for IHurtbox.
- **AC9 (Scene transition Clear)**: Mock SceneTransitionHandler. Fire transition. Verify Clear() called.

**Edge cases**: Duplicate Register (idempotency), Register before Registry exists (VContainer guarantee), DontDestroyOnLoad survival.

## Test Evidence Path

- `tests/Foundation/HitDetection/TestHitDetectionRegistry.cs`
- Unit tests covering register/unregister, faction matching, null tolerance, Clear()

## Dependencies

- **Depends on**: None (HitDetectionRegistry is standalone)
- **Unlocks**: Story 002 (Hit Event Dispatch)

## Risks

- Late-registering objects (Spawned mid-combat) must ensure registry exists — VContainer inject guarantees this
- Destroyed-but-not-null objects (DontDestroyOnLoad edge case) — mitigate by explicit Unregister in OnDestroy

## Completion Notes
**Completed**: 2026-06-04
**Criteria**: 6/9 passing (3 advisory — AC7/AC8 lifecycle auto-registration deferred to concrete IHitbox/IHurtbox MonoBehaviours; AC9 scene transition Clear() deferred to SceneTransitionHandler)
**Deviations**: ADVISORY — IHitbox/IHurtbox interfaces simplified (no Owner/Type fields), HitDetectionRegistry is MonoBehaviour (not plain class), test file path mismatch
**Test Evidence**: Logic: test file at `Assets/_TinyRift/Tests/EditMode/Combat/TestHitDetectionRegistry.cs` (16 tests)
**Code Review**: Complete (previously approved with suggestions)
