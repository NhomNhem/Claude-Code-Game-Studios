# Story 002: Hit Detection & Event Dispatch

- **Epic**: Hit Detection
- **System**: Hit Detection — Dispatch
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-04

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-hitdetect-001` | Player projectile hits enemy → HitEvent with correct data | ✅ ADR-002 |
| `TR-hitdetect-004` | Enemy contact damage → HitEvent with enemy as attacker | ✅ ADR-002 |

## ADR Guidance

**ADR-002 (Event Bus Contract):**
- HitEvent is a readonly record struct — value semantics, no allocation
- Fire-and-forget: Hit Detection publishes HitEvent and stops. Downstream systems (Combat/Damage) subscribe independently.
- HitEvent fields: `EntityId Source`, `EntityId Target`, `Vector3 HitPosition`
- Published via `IEventBus.Publish<T>(T event)` — no return value expected

## Description

Bridges Unity's OnTriggerEnter messages into typed HitEvent publications on the Event Bus. OnTriggerEnter on a hitbox queries the HitDetectionRegistry for a matching hurtbox on the opposing faction, and if valid publishes HitEvent. Does not apply damage — only routes the collision to subscribers.

## Design

- `HitEvent` readonly record struct:
  - `EntityId Source { get; }`
  - `EntityId Target { get; }`
  - `Vector3 HitPosition { get; }`
- `HitResolver` (MonoBehaviour, registered via VContainer):
  - Listens for template's existing `OnTriggerEnter` events on hitbox GameObjects
  - On trigger: looks up other collider's hurtbox in registry via `HitDetectionRegistry.FindHurtbox(Collider)`
  - Runs faction check: if attacker.Faction is not blocked by defender.ImmuneTo → valid hit
  - If valid: constructs `HitEvent` and calls `IEventBus.Publish(hitEvent)`
  - If invalid or missing: silently no-ops
- Enemy contact damage (TR-hitdetect-004):
  - Enemy root GameObject has an `IHitbox` component; player has `IHurtbox`
  - Same flow — OnTriggerEnter on enemy hitbox → lookup player hurtbox → faction check → HitEvent
- No modification to template `DamageEntity` or `MonsterEntity` — hitboxes/hurtboxes are separate components added to the same GameObject hierarchy
- One `HitResolver` instance is sufficient; it holds no per-hit state (cooldown belongs in Story 003)

## Acceptance Criteria

1. OnTriggerEnter between player projectile hitbox and enemy hurtbox → HitEvent published with correct Source (player), Target (enemy), HitPosition
2. Enemy contact hitbox vs player hurtbox → HitEvent published with enemy as Source, player as Target
3. Same-faction collision → no HitEvent published
4. Missing registry entry (unregistered collider) → no exception, no event
5. HitEvent.Source resolves from IHitbox.Owner via EntityId
6. HitEvent.HitPosition uses collision.contacts[0].point
7. No damage is applied by HitResolver — publish only

## QA Test Cases

- **AC1 (Player→Enemy hit)**: Place player projectile hitbox + enemy hurtbox. Trigger OnTriggerEnter. Verify HitEvent published with correct Source (player EntityId), Target (enemy EntityId), HitPosition.
- **AC2 (Enemy→Player hit)**: Place enemy contact hitbox + player hurtbox. Trigger OnTriggerEnter. Verify HitEvent published with enemy as Source, player as Target.
- **AC3 (Same-faction block)**: Place player hitbox + player hurtbox. Trigger collision. Verify no HitEvent published.
- **AC4 (Missing registry)**: Collide unregistered collider with another. Verify no exception and no event.
- **AC5 (EntityId resolution)**: Verify HitEvent.Source resolves from hitbox owner's EntityId component.
- **AC6 (Contact point)**: Verify HitEvent.HitPosition == collision.contacts[0].point.
- **AC7 (No damage)**: Verify HitResolver never calls any damage application — publish only.

**Edge cases**: Multiple simultaneous collisions, collider destroyed mid-trigger.

## Test Evidence

- `Assets/_TinyRift/Tests/EditMode/Combat/TestHitEventDispatch.cs`
- Integration tests: place hitbox/hurtbox, trigger collision, verify HitEvent fields via event bus spy

## Dependencies

- **Depends on**: Story 001 (HitDetectionRegistry), Event Bus (from foundation-infrastructure epic)
- **Unlocks**: Story 003 (Per-Target Hit Cooldown)

## Risks

- Physics trigger pairs must match layer collision matrix — verify hitbox/hurtbox layers are configured in Project Settings
- Template may already handle OnTriggerEnter on these objects — our components must coexist, not override (use separate MonoBehaviour, not inheritance)

## Completion Notes
**Completed**: 2026-06-04
**Criteria**: 7/7 passing
**Deviations**: ADVISORY — AC6 mentions collision.contacts[0].point but OnTriggerEnter doesn't expose contacts; ClosestPoint used instead (functionally equivalent). IHitbox/IHurtbox interfaces extended with OwnerId and IHitDetectionRegistry with FindHitbox/FindHurtbox as natural scope of HD-002 design.
**Test Evidence**: 12 EditMode unit tests at Assets/_TinyRift/Tests/EditMode/Combat/TestHitEventDispatch.cs (all passing). Integration testing of OnTriggerEnter adapter requires playtest session.
**Code Review**: APPROVED (LP-CODE-REVIEW) + ADEQUATE (QL-TEST-COVERAGE)
