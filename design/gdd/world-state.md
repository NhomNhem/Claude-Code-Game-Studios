# World State

> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED 2026-05-29
> **Status**: Designed
> **Author**: game-designer
> **Last Updated**: 2026-05-29
> **Implements Pillar**: P4 (World Reactivity) — the world remembers what you've done.

## Overview

The World State system manages persistent world progression: which zones are unlocked, which are completed, and what visual restoration state each zone has achieved. It loads `ZoneCompletionEntry[]` from Save/Profile on boot, maintains a runtime registry of per-zone state, and on Victory marks the current zone as completed, unlocks the next zone in sequence, and publishes `ZoneRestoredEvent` to the Event Bus for VFX/Post-Processing consumption. The system mediates between Save/Profile (persistence layer) and consuming systems (Minimap, Hero/Zone Unlock) — it is the runtime authority on world progression state.

## Player Fantasy

The player never interacts with World State directly. They experience it as the quiet conviction that their progress matters — zones stay completed, the next zone is waiting, and the world carries visible evidence of what they've done. When color snaps back in a completed zone, it's not a fanfare — it's the world exhaling. The player doesn't think "state updated." They think "it's whole again here."

## Detailed Design

### Core Rules

1. **Boot load** — On app start, `WorldStateService` loads `ZoneCompletionEntry[]` from Save/Profile via `IPersistStateService.LoadPersistentAsync()`. Builds a runtime `Dictionary<string, ZoneState>` indexed by `zoneId`.

2. **Zone 1 guarantee** — `zone_fractured_pass` is always unlocked. If `LoadPersistentAsync()` returns no entry for Fractured Pass (fresh profile), the service creates one with `isUnlocked = true` and writes it to Save/Profile.

3. **Linear unlock sequence** — MVP uses a hardcoded sequence: Fractured Pass → Crystal Caverns → Ash Circle. Ash Circle is terminal (no zone after it).

4. **Victory handling** — On receiving `GameStateChanged(InRun → Victory)`:
   - Mark current zone as `completed = true`
   - Update `bestSurvivalTimeSeconds` (max-wins), `totalKillsInZone` (max-wins)
   - Unlock next zone in sequence (if not terminal)
   - Call `IPersistStateService.AddUnlockAsync()` to persist
   - Publish `ZoneRestoredEvent(zoneId, RestoreLevel.Full)` to Event Bus

5. **Camp growth level** — Deferred from MVP. `RestoreLevel.Full` is always used for MVP.

6. **ZoneState runtime model**:
```csharp
public class ZoneState
{
    public string zoneId;
    public bool isUnlocked;
    public bool completed;
    public int bestSurvivalTimeSeconds;
    public int totalKillsInZone;
    public long lastModified;
}
```

7. **Query API** — `IWorldStateService` exposes:
   - `bool IsZoneUnlocked(ZoneId zoneId)`
   - `bool IsZoneCompleted(ZoneId zoneId)`
   - `ZoneState GetZoneState(ZoneId zoneId)`
   - `IReadOnlyList<ZoneState> GetAllZoneStates()`

8. **Re-entrancy guard** — A `_isProcessingVictory` flag prevents double-processing if rapid Victory events arrive while the async persist+publish cycle is in progress. Second event is silently ignored.

### States and Transitions

| Phase | Description |
|-------|-------------|
| Uninitialized | Initial state before load |
| Initializing | `LoadPersistentAsync()` in progress |
| Ready | Runtime state available for queries. Normal operating state. |
| VictoryProcessing | Transient substate during Victory handling (async persist + event publish). ~100ms. Re-entrancy guard active. |

One-way: `Uninitialized → Initializing → Ready`. `Ready ⇄ VictoryProcessing` (cycles on each zone completion).

All transitions always succeed — an empty dictionary with Zone 1 unlocked is a valid Ready state (fresh profile, no zones completed).

### Interactions with Other Systems

| System | Direction | What Flows | Contract |
|--------|-----------|------------|----------|
| Save/Profile (#10) | Inbound/Outbound | Loads `ZoneCompletionEntry[]` on boot. Writes unlock/completion via `AddUnlockAsync()` | `IPersistStateService.AddUnlockAsync(zoneId)` on Victory |
| Event Bus (#5) | Inbound | Subscribes to `GameStateChanged(InRun → Victory)` for zone completion trigger | Event Bus subscription |
| Event Bus (#5) | Outbound | Publishes `ZoneRestoredEvent(zoneId, RestoreLevel.Full)` on Victory | `Void ZoneRestoredEvent(ZoneId, RestoreLevel)` |
| VFX System (#15) | Outbound (via Event Bus) | Receives `ZoneRestoredEvent` for zone restore sweep VFX | Indirect — via Event Bus |
| Post-Processing | Outbound (via Event Bus) | Receives `ZoneRestoredEvent` for color grading shift | Indirect — via Event Bus |
| Minimap (#37) | Outbound | Zone unlock/completion state for map display | `IWorldStateService.GetZoneState()` (Vertical Slice) |
| Hero/Zone Unlock (#39) | Outbound | Zone unlock status for camp UI | `IWorldStateService.IsZoneUnlocked()` (Vertical Slice) |

## Formulas

None. World State tracks boolean and numeric state with merge rules defined in Save/Profile's conflict resolution. No mathematical calculations.

## Edge Cases

- **If fresh profile (no save data)**: Dictionary loads empty. `GetOrCreateZoneOne()` seeds Zone 1 (Fractured Pass) as unlocked and incomplete. All other zones locked. No progression possible until first Victory.

- **If Victory fires on an already-completed zone**: Best values update (max-wins for `bestSurvivalTimeSeconds`, `totalKillsInZone`). Zone stays completed. No unlock ripple (next zone already unlocked or terminal). The re-entrancy guard must only block duplicate in-flight processing, not subsequent legitimate Victories on the same zone.

- **If Victory fires on terminal zone (Ash Circle — no next zone)**: The "unlock next zone" step checks whether `nextZoneId` exists in the sequence. If not found, it is silently skipped. Zone marked completed, best values updated, `ZoneRestoredEvent` published normally.

- **If double Victory events arrive simultaneously**: First event sets `_isProcessingVictory = true` before any `await`, processes fully, publishes event. Second event checks `_isProcessingVictory` and exits immediately. `_isProcessingVictory` must be set synchronously, not after an async operation.

- **If Save load fails (deserialize throws)**: Fallback to fresh-profile behavior — Zone 1 created, all others locked. Previously completed zones are lost. Error is logged. The game continues without crashing.

- **If next zone is already unlocked on Victory (from sync merge)**: `AddUnlockAsync()` on an already-unlocked zone is idempotent. Setting `isUnlocked = true` on an already-true field produces no state change. Safe to run unconditionally.

- **If boot with all 3 zones already unlocked**: All zones load as unlocked and incomplete. Linear progression (`IsZoneCompleted(prev)`) still gates zone entry at the Zone Definition / Camp level. Prematurely unlocked zones are harmless — the player cannot enter them until they complete the previous zone.

- **If all 3 zones are already completed on boot**: All zones marked completed and unlocked. `GetAllZoneStates()` returns full terminal set. No further progression possible until a content update adds more zones. UI must handle "all zones completed" gracefully (show completion, no error).

- **If player re-enters an already-completed zone**: The zone loads and plays normally. Another Victory updates best values again. The player can farm completions on any zone. Edge: if Hero Camp progression is ever tied to *first* completion, the `completed` flag is monotonic — it never regresses.

## Dependencies

### Hard Dependencies

| System | # | Nature |
|--------|---|--------|
| Save/Profile Persistence | 10 | Loads `ZoneCompletionEntry[]` on boot via `LoadPersistentAsync()`. Writes unlocks/completions on Victory via `AddUnlockAsync()`. |
| Event Bus | 5 | Subscribes to `GameStateChanged(InRun → Victory)` for zone completion trigger. Publishes `ZoneRestoredEvent` for downstream consumers. |

### Soft Dependencies

| System | # | Nature |
|--------|---|--------|
| VFX System | 15 | Consumes `ZoneRestoredEvent` for zone restore sweep VFX (indirect, via Event Bus). |
| Post-Processing | — | Consumes `ZoneRestoredEvent` for color grading shift (indirect, via Event Bus). |
| Minimap | 37 | Reads zone unlock/completion state via `IWorldStateService` (Vertical Slice). |
| Hero/Zone Unlock | 39 | Reads zone unlock status via `IWorldStateService` (Vertical Slice). |
| Zone Definition System | 12 | Game-flow: zone unlock state determines which zones the player can enter. No direct code coupling. |

### Bidirectional Consistency

- Save/Profile lists "World State — Reads/writes zone completions" and "World State: Hard — Reads/writes `WorldSaveData`" (✓ matches this GDD)
- Event Bus lists World State as producer of `ZoneRestoredEvent` (✓ matches this GDD)
- Zone Definition System lists "World State (#13) — None; Zone Definition does not read/write world state" and "World State owns ZoneCompletionEntry" (✓ consistent)

## Tuning Knobs

None. The MVP zone unlock sequence (Fractured Pass → Crystal Caverns → Ash Circle) is hardcoded. No tunable values exist. Future tuning knobs may include: configurable zone unlock sequence, per-zone completion thresholds for restorative effects, and visual restoration tiers. All deferred.

## Acceptance Criteria

### Boot and Load

- **AC1** — **GIVEN** a fresh profile (no save data), **WHEN** `WorldStateService` initializes, **THEN** `zone_fractured_pass` is unlocked AND `IsZoneUnlocked(FracturedPass)` returns `true` AND `IsZoneCompleted(FracturedPass)` returns `false`.

- **AC2** — **GIVEN** save data containing a completed `zone_crystal_caverns` entry, **WHEN** `WorldStateService` initializes, **THEN** `IsZoneCompleted(CrystalCaverns)` returns `true` AND `GetZoneState(CrystalCaverns).bestSurvivalTimeSeconds` matches the save value.

- **AC3** — **GIVEN** Save load throws a deserialization exception, **WHEN** `WorldStateService` initializes, **THEN** the error is logged AND fallback state is used (Zone 1 unlocked, all others locked and incomplete).

### Victory Handling

- **AC4** — **GIVEN** the player is in `zone_fractured_pass` AND `GameStateChanged(Victory)` fires, **WHEN** World State processes the event, **THEN** `IsZoneCompleted(FracturedPass)` returns `true` AND `IsZoneUnlocked(CrystalCaverns)` returns `true` (next zone unlocked).

- **AC5** — **GIVEN** the player completes `zone_ash_circle` (terminal zone), **WHEN** Victory is processed, **THEN** `IsZoneCompleted(AshCircle)` returns `true` AND no exception is thrown when attempting to unlock the next zone AND `ZoneRestoredEvent` is still published.

- **AC6** — **GIVEN** the player completes an already-completed zone, **WHEN** Victory is processed, **THEN** best values are updated (if new values are higher) AND zone remains completed AND no new zone unlock occurs.

- **AC7** — **GIVEN** two `GameStateChanged(Victory)` events fire in rapid succession, **WHEN** the first event starts processing, **THEN** `_isProcessingVictory` is set synchronously before any `await` AND the second event exits immediately without processing.

### Query API

- **AC8** — **GIVEN** Zone 1 is unlocked and Zone 2 is locked, **WHEN** `IsZoneUnlocked(FracturedPass)` is called, **THEN** returns `true`. **WHEN** `IsZoneUnlocked(CrystalCaverns)` is called, **THEN** returns `false`.

- **AC9** — **GIVEN** a zone is completed, **WHEN** `IsZoneCompleted(zoneId)` is called, **THEN** returns `true`.

- **AC10** — **GIVEN** any zone, **WHEN** `GetZoneState(zoneId)` is called, **THEN** returns a `ZoneState` with `zoneId`, `isUnlocked`, `completed`, `bestSurvivalTimeSeconds`, `totalKillsInZone`, and `lastModified` matching the runtime state.

- **AC11** — **GIVEN** all 3 zones loaded, **WHEN** `GetAllZoneStates()` is called, **THEN** returns an `IReadOnlyList` of 3 `ZoneState` entries.

### Event Publishing

- **AC12** — **GIVEN** Victory is processed on a zone, **WHEN** the event is published, **THEN** `ZoneRestoredEvent` is sent to the Event Bus with the correct `ZoneId` and `RestoreLevel.Full`.
