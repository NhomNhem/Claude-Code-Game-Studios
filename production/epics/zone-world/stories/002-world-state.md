# Story 002: World State

- **Epic**: Zone & World
- **System**: World State
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-worldstate-001` | Zone unlock/restore state persisted | ✅ ADR-001 |
| `TR-worldstate-002` | Zone completion publishes restoration event | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `IWorldStateService` interface singleton in `TinyRiftScope`
- Subscribes to `GameStateChanged` for Victory detection
- Publishes `ZoneRestoredEvent` to Event Bus

**Control Manifest (Core Layer):**
- Persistence via `IPersistStateService` (load on boot, write on Victory)
- Zone 1 (Fractured Pass) always unlocked on fresh profile
- Re-entrancy guard on Victory processing

## Description

Implement the World State service: load `ZoneCompletionEntry[]` from Save/Profile on boot, maintain runtime `Dictionary<string, ZoneState>` of per-zone progression, handle Victory transitions by marking zones complete and unlocking the next zone in sequence, and publish `ZoneRestoredEvent` for VFX consumption.

## Design

### WorldStateService

```csharp
public interface IWorldStateService
{
    bool IsZoneUnlocked(ZoneId zoneId);
    bool IsZoneCompleted(ZoneId zoneId);
    ZoneState GetZoneState(ZoneId zoneId);
    IReadOnlyList<ZoneState> GetAllZoneStates();
}
```

### Boot Load

1. `InitializeAsync()` calls `LoadPersistentAsync()` to get `ZoneCompletionEntry[]`
2. Build `Dictionary<string, ZoneState>` from entries
3. If empty (fresh profile): seed Zone 1 (Fractured Pass) as `isUnlocked = true, completed = false`
4. Write seed data to Save/Profile

### Victory Handling

On `GameStateChanged(InRun → Victory)`:
1. Set `_isProcessingVictory = true` (synchronous, before any await)
2. Look up current zone from context
3. Mark zone `completed = true`
4. Update `bestSurvivalTimeSeconds` (max-wins), `totalKillsInZone` (max-wins)
5. Unlock next zone in sequence (Fractured Pass → Crystal Caverns → Ash Circle)
6. If terminal zone (Ash Circle): skip unlock step silently
7. Call `IPersistStateService.AddUnlockAsync()` to persist
8. Publish `ZoneRestoredEvent(zoneId, RestoreLevel.Full)` to Event Bus
9. Set `_isProcessingVictory = false`

### Linear Unlock Sequence

```csharp
private static readonly string[] ZoneSequence =
{
    "zone_fractured_pass",
    "zone_crystal_caverns",
    "zone_ash_circle"
};
```

### Re-Entrancy Guard

- `_isProcessingVictory` flag set synchronously in the event handler
- Second Victory event while processing → silently ignored
- Flag cleared after async persist + event publish completes

## Acceptance Criteria

1. **GIVEN** a fresh profile (no save data), **WHEN** `WorldStateService` initializes, **THEN** `zone_fractured_pass` is unlocked AND `IsZoneUnlocked(FracturedPass)` returns `true` AND `IsZoneCompleted(FracturedPass)` returns `false`.
2. **GIVEN** save data containing a completed `zone_crystal_caverns` entry, **WHEN** initialized, **THEN** `IsZoneCompleted(CrystalCaverns)` returns `true` AND `GetZoneState(CrystalCaverns).bestSurvivalTimeSeconds` matches save value.
3. **GIVEN** player is in `zone_fractured_pass` AND `GameStateChanged(Victory)` fires, **WHEN** processed, **THEN** `IsZoneCompleted(FracturedPass)` returns `true` AND `IsZoneUnlocked(CrystalCaverns)` returns `true`.
4. **GIVEN** player completes `zone_ash_circle` (terminal), **WHEN** Victory is processed, **THEN** `IsZoneCompleted(AshCircle)` returns `true` AND no exception on next-zone unlock AND `ZoneRestoredEvent` is published.
5. **GIVEN** two `GameStateChanged(Victory)` events in rapid succession, **WHEN** first starts processing, **THEN** `_isProcessingVictory` is set synchronously before any `await` AND second event exits immediately.
6. **GIVEN** Victory is processed, **WHEN** event is published, **THEN** `ZoneRestoredEvent` is sent with correct `ZoneId` and `RestoreLevel.Full`.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/ZoneWorld/WorldStateTests.cs`
- All 6 acceptance criteria as individual test methods
- Mock `IPersistStateService`, mock Event Bus for Victory subscription and ZoneRestoredEvent publication

## Dependencies

- **Zone Story 001** — Zone Definition System (ZoneId struct, zone sequence)
- **Save Story 001** — Core Persistence Layer (IPersistStateService for loading/writing zone state)
- **Event Bus** — GameStateChanged subscription, ZoneRestoredEvent publication

## Unlocks

- Wave Spawning System (zone completion gates next zone)
- Hero Camp (zone unlock display)

## Risks

- **LOW**: Re-entrancy guard synchronously blocks duplicate Victory events. Mitigation: this is intentional — Victory processing is fast (< 1 frame) and double-triggers are edge-case only.
