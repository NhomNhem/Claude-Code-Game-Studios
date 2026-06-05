# Story 001: Status Effect Service Core

- **Epic**: Status Effect System
- **System**: Status Effect System
- **Type**: Logic
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-statusfx-001` | Per-entity status tracking (frozen/burned/stunned) | ✅ ADR-001 |
| `TR-statusfx-003` | API: `ApplyStatus(StatusType, EntityId)`, `GetActiveStatuses(EntityId)` | ✅ ADR-001, ADR-004 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `IStatusEffectService` registers as interface singleton in `GameplayLifetimeScope`
- Consumed by Hit Detection, Enemy AI, Boss Encounter systems

**ADR-004 (Time System):**
- Duration tracking via `ITimeManager` elapsed time queries
- Tick timers for Burn DOT resolved via `ITimeManager`
- Pause-safe: status timers respect time scale

**Control Manifest (relevant rules):**
- `StatusInstance` tracks: target entity, status type, remaining duration, tick timer, tick count
- Per-entity status dictionary for O(1) lookups
- All statuses cleared on entity death or zone transition

## Description

Implement the core `IStatusEffectService` — a pure data layer that tracks active elemental statuses per entity. Supports duration-based statuses with tick timers via `ITimeManager`. Per-entity dictionary provides O(1) `ApplyStatus()`, `GetActiveStatuses()`, and `ClearAll()` operations. Status instances are cleared on entity death and zone transition. No element-specific behavior — this story provides the storage and lifecycle infrastructure only.

## Design

```csharp
public interface IStatusEffectService
{
    void ApplyStatus(StatusType type, EntityId target, float duration, float tickInterval = 0, float tickDamageMultiplier = 0);
    IReadOnlyList<StatusInstance> GetActiveStatuses(EntityId target);
    bool HasStatus(EntityId target, StatusType type);
    void ClearStatus(EntityId target, StatusType type);
    void ClearAll(EntityId target);
    void ClearAllEntities();
}

public readonly struct StatusInstance
{
    public StatusType Type { get; }
    public EntityId Target { get; }
    public float RemainingDuration { get; }
    public float TickTimer { get; }
    public int TickCount { get; }
    public bool IsExpired => RemainingDuration <= 0;
}

public enum StatusType
{
    Burn,
    Slow,
    Freeze,
    Stun
}
```

### Internal Data Model

```csharp
private class StatusEntry
{
    public StatusType Type;
    public EntityId Target;
    public float Duration;
    public float TickInterval;
    public float TickDamageMultiplier;
    public float ElapsedSinceTick;
    public int TickCount;
}
```

```csharp
private Dictionary<EntityId, List<StatusEntry>> _activeStatuses;
```

### Lifecycle

- `ApplyStatus()`: Add or refresh status entry. If already active, reset duration. Freeze cooldown tracked separately.
- `Update(deltaTime)`: Tick down durations. For Burn, accumulate tick timer and trigger DOT when interval reached.
- `ClearStatus()`: Remove specific status by type for an entity.
- `ClearAll(entity)`: Remove all statuses for an entity (death).
- `ClearAllEntities()`: Remove all statuses (zone transition).

### Time Integration

- All duration and tick tracking uses `ITimeManager.DeltaTime` (respects pause and time scale)
- No direct `Time.deltaTime` usage

### Status Removal Triggers

- Duration expiry (automatic during Update)
- Entity death (via `ClearAll(entity)`)
- Zone transition (via `ClearAllEntities()`)
- Manual removal (via `ClearStatus(entityId, type)`)

## Acceptance Criteria

1. **ApplyStatus creates entry**: After `ApplyStatus(Burn, entityA, 3.0f)`, `GetActiveStatuses(entityA)` returns a list containing a Burn entry.
2. **Duration countdown**: After applying a 2.0s status and advancing time by 1.0s, `RemainingDuration` is 1.0s.
3. **Duration expiry removes status**: After duration reaches 0, the status is no longer in `GetActiveStatuses()`.
4. **Refresh duration**: Re-applying the same status resets duration to the new value.
5. **ClearStatus removes specific**: `ClearStatus(entityA, Burn)` removes only Burn; other statuses on entityA remain.
6. **ClearAll removes all**: `ClearAll(entityA)` removes every status for entityA.
7. **ClearAllEntities removes everything**: After `ClearAllEntities()`, no entity has any active statuses.
8. **HasStatus returns correct**: `HasStatus(entityA, Burn)` is true after applying Burn, false after removal.
9. **Non-existent entity returns empty**: `GetActiveStatuses(nonexistentId)` returns empty list, does not throw.
10. **ITimeManager integration**: All timing uses `ITimeManager.DeltaTime`, not `Time.deltaTime`.
11. **Tick timer accumulates**: Burn with 1.0s tick interval accumulates `ElapsedSinceTick` correctly each frame.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/StatusEffectSystem/StatusEffectServiceCoreTests.cs`
- Apply/query/clear operations for all status types
- Duration tracking and expiry
- Time infrastructure decoupling (ManualTimeProvider)

## Dependencies

- **ITimeManager (from foundation-infrastructure)** — duration tracking, tick timers, pause-safe delta time

## Unlocks

- Status Story 002 (Elemental Status Implementations)

## Risks

- **LOW**: Per-entity `List<StatusEntry>` could grow unbounded if many statuses per entity. Mitigation: max 3 elements (one per element type per entity). Cleared on death.
- **LOW**: `Update()` called every frame — trivial cost for dictionary iteration with small N.
