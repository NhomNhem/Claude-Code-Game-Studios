# Story 002: Elemental Status Implementations

- **Epic**: Status Effect System
- **System**: Status Effect System
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-statusfx-002` | Tick countdowns and stack management (per-element implementations) | ✅ ADR-002, ADR-004 |

## ADR Guidance

**ADR-002 (Event Bus Contract):**
- Consumes `DamageDealtEvent` to resolve status effects by element type
- Burn DOT publishes `DamageDealtEvent` with `DamageType = StatusEffect`

**ADR-004 (Time System):**
- Tick countdowns managed via `ITimeManager`
- Duration tracking for all three element types

**Control Manifest (relevant rules):**
- `DamageDealtEvent` with `ElementType.None` applies no status
- Boss immunity: status silently rejected if entity declares immunity
- Freeze cooldown tracked separately from status duration
- Player receives NO status effects in MVP

## Description

Implement the element-to-status mapping layer that consumes `DamageDealtEvent` and applies the correct elemental status via `IStatusEffectService`. Fire applies Burn (DoT with tick damage), Ice applies Slow (move speed -40%, attack rate -20%) upgrading to Freeze (rooted, 2x damage) at <50% HP, Lightning applies Stun (rooted, 0.5s). Burn DOT publishes its own `DamageDealtEvent` for the Damage & Health System. Boss immunity and freeze cooldown are enforced.

## Design

### Element → Status Mapping

| Element | Status | Effect | Tick Interval | Duration | Stacking |
|---------|--------|--------|---------------|----------|----------|
| Fire | Burn | DOT: 5% of base damage per tick | 1.0s | 3.0s | Refresh duration |
| Ice | Slow | Move speed -40%, attack rate -20% | — (continuous) | 2.0s | Refresh duration |
| Ice (<50% HP) | Freeze | Rooted, no actions, 2x next hit damage | — | 1.5s | Cannot re-freeze (5s cooldown) |
| Lightning | Stun | Rooted, no actions | — | 0.5s | Refresh duration |

### Burn Tick System

```csharp
// In StatusEffectService.Update():
foreach (var status in _activeStatuses.SelectMany(kvp => kvp.Value))
{
    if (status.Type != StatusType.Burn) continue;
    status.ElapsedSinceTick += timeManager.DeltaTime;
    while (status.ElapsedSinceTick >= status.TickInterval)
    {
        status.ElapsedSinceTick -= status.TickInterval;
        status.TickCount++;
        float tickDamage = status.TickDamageMultiplier * _lastDamageAmount[status.Target];
        eventBus.Publish(new DamageDealtEvent(
            status.Target, tickDamage, DamageType.StatusEffect, ElementType.None
        ));
    }
}
```

### Freeze Cooldown

```csharp
private Dictionary<EntityId, float> _freezeCooldowns; // seconds remaining

// On freeze expire or remove:
_freezeCooldowns[target] = 5.0f;

// On ice hit when target HP < 50%:
if (_freezeCooldowns.TryGetValue(target, out float remaining) && remaining > 0)
    ApplyStatus(StatusType.Slow, target, 2.0f); // downgrade to slow
else
    ApplyStatus(StatusType.Freeze, target, 1.5f);
```

### Boss Immunity

```csharp
public bool IsImmuneTo(EntityId target, StatusType type)
{
    // Check via IStatusImmunityProvider (injected)
    return _immunityProvider?.IsImmune(target, type) ?? false;
}
```

Non-elemental damage (`ElementType.None`) exits early with no status application.

## Acceptance Criteria

1. **Fire applies Burn**: When `DamageDealtEvent` with `ElementType.Fire` fires, a Burn status is applied to the target.
2. **Burn ticks deal DOT**: Every tick interval, Burn publishes `DamageDealtEvent` with 5% of original damage and `DamageType = StatusEffect`.
3. **Burn duration refresh**: Re-applying Burn while active resets duration to 3.0s.
4. **Burn expires**: After 3.0s without refresh, Burn is removed.
5. **Ice applies Slow**: When `DamageDealtEvent` with `ElementType.Ice` fires, Slow is applied (move speed -40%, attack rate -20%).
6. **Ice at <50% HP applies Freeze**: If target HP < 50%, Ice applies Freeze instead of Slow (rooted, 2x next damage).
7. **Freeze cooldown**: Freeze cannot be reapplied within 5s of expiry — downgrades to Slow.
8. **Lightning applies Stun**: When `DamageDealtEvent` with `ElementType.Lightning` fires, Stun is applied (rooted, 0.5s).
9. **Duration refresh on re-apply**: Re-applying the same status refreshes duration (no stacking).
10. **Status cleared on death**: When an entity dies, all active statuses are removed.
11. **Status cleared on zone transition**: All active status instances are cleared.
12. **Non-elemental damage no-op**: `DamageDealtEvent` with `ElementType.None` applies no status.
13. **Boss immunity**: If a boss declares immunity to a status type, that status is silently rejected.
14. **Status application before lethal**: Enemy about to die still receives status on the frame of lethal damage.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/StatusEffectSystem/ElementalStatusImplementationTests.cs`
- Fire: Burn tick damage values and timing
- Ice: Slow vs Freeze threshold at 50% HP, freeze cooldown timing
- Lightning: Stun duration and refresh
- Boss immunity rejection
- Edge cases (Freeze cooldown, non-elemental, death clear)

## Dependencies

- **Status Story 001** — `IStatusEffectService` core, `StatusInstance`, per-entity tracking
- **Event Bus** — Consumes `DamageDealtEvent`, publishes Burn DOT `DamageDealtEvent`
- **ITimeManager (from foundation-infrastructure)** — tick countdown, duration tracking

## Unlocks

- **Damage & Health System** — receives Burn DOT `DamageDealtEvent` publications
- **Enemy AI** — reads `HasStatus()` for movement/action modification
- **Boss Encounter** — declares status immunity per boss type

## Risks

- **MEDIUM**: Burn DOT publishes `DamageDealtEvent` which could trigger infinite loops if Damage & Health re-publishes. Mitigation: DOT events use `DamageType = StatusEffect` — Damage & Health must NOT re-fire status effects from StatusEffect damage type.
- **LOW**: Freeze cooldown of 5s with typical combat pacing means freeze is at most once per engagement. Acceptable — freeze is a bonus, not a rotation requirement.
