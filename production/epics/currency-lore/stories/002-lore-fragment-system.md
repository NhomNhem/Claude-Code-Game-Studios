# Story 002: Lore Fragment System

- **Epic**: Currency & Lore
- **System**: Lore Fragment System
- **Type**: Integration
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-lore-001` | Fragment data storage and retrieval | ✅ ADR-001 |
| `TR-lore-002` | Auto-collect on elite/boss kill | ✅ ADR-002 |
| `TR-lore-003` | Codex data provider for fragment display | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `ILoreFragmentService` registers as interface singleton in TinyRiftScope
- Fragment data defined as `MemoryFragmentData` ScriptableObjects
- Codex query layer reads via injected service, not direct data access

**ADR-002 (Event Bus Contract):**
- Consumes `EntityDiedEvent` with `isConfirmedDeath: bool` and `eliteTypeId: string`
- Publishes `LoreFragmentCollectedEvent(fragmentId, zoneId)` for HUD toasts and VFX ripple

**Control Manifest (relevant rules):**
- Fragment data Model reserved fields (`worldStateEffect`, `mechanicalRewardId`) are `None` / empty in MVP
- Union-merge persistence: `collectedLoreFragmentIds = collected.Union(runFragments).Distinct().ToList()`
- Read state is local-only, never synced

## Description

Implement the Lore Fragment System — auto-collects memory fragments on elite/boss death (if not already collected), persists via Save/Profile with union-merge deduplication, publishes `LoreFragmentCollectedEvent`, and provides a read-only query layer for the Codex UI. Manages first-kill guarantee vs repeat generic pool logic with dimmed flash visual when all fragments are exhausted.

## Design

```csharp
public interface ILoreFragmentService
{
    IReadOnlyList<string> GetCollectedFragmentIds();
    MemoryFragmentData GetFragmentById(string id);
    List<MemoryFragmentData> GetFragmentsByZone(string zoneId);
    List<MemoryFragmentData> GetFragmentsByFigure(string figureId);
    int GetUncollectedCount();
    bool IsFragmentCollected(string id);
    bool GetFragmentReadState(string id);
    void MarkFragmentRead(string id);
}
```

### Collection Flow

1. Entity dies → `EntityDiedEvent` with `isConfirmedDeath == true`
2. Check entity `eliteTypeId` against `killedEliteTypesThisRun` and `collectedLoreFragmentIds`
3. First-kill guarantee → unique fragment. Repeat → generic pool entry. Exhausted → dimmed flash only
4. Credit: `AddLoreFragmentAsync(fragmentId)` + append to `killedEliteTypesThisRun`
5. Publish `LoreFragmentCollectedEvent(fragmentId, zoneId)`
6. Consumers: camera micro-freeze, fragment tablet, ripple VFX, audio stinger, HUD toast

### Persistence

- `collectedLoreFragmentIds`: `List<string>` in `persistent.json` (union-merge)
- `loreFragmentIdsThisRun`: `List<string>` in `runstate.json` (ephemeral)
- `killedEliteTypesThisRun`: `List<string>` in `runstate.json` (reset on run start)
- Mid-run `AddLoreFragmentAsync()` for crash safety
- Run-end flush: `collected = collected.Union(loreFragmentIdsThisRun).Distinct().ToList()`

### Codex Query Layer

```csharp
GetAllFragments() → List<MemoryFragmentData>
GetCollectedFragmentIds() → List<string>
GetFragmentById(string id) → MemoryFragmentData
GetFragmentsByZone(string zoneId) → List<MemoryFragmentData>
GetFragmentsByFigure(string figureId) → List<MemoryFragmentData>
GetUncollectedCount() → int
GetFragmentReadState(string id) → bool
MarkFragmentRead(string id)
```

Read state transitions from "unread" to "read" when player clicks the translate toggle on the fragment card.

## Acceptance Criteria

1. **First-kill elite fragment**: When an elite dies (first time, not yet collected), `AddLoreFragmentAsync()` is called and `LoreFragmentCollectedEvent` publishes.
2. **Boss story-critical fragment**: When a boss dies, its unique story-critical fragment is credited.
3. **Repeat kill generic pool**: When the same elite type dies again, a generic "Fragment of a Life" entry is credited if pool remains.
4. **Unconfirmed death ignored**: When `isConfirmedDeath = false`, no fragment is credited and no event publishes.
5. **Persistence across runs**: Fragment collected in run 1 persists and is `GetCollectedFragmentIds()` visible in run 2.
6. **Crash recovery**: Mid-run fragment collected before crash is present in `GetCollectedFragmentIds()` after relaunch.
7. **Duplicate deduplication**: Union-merge prevents duplicate fragment IDs in persistent storage.
8. **Codex uncollected count**: `GetUncollectedCount()` returns correct count of uncollected fragments.
9. **New badge before read**: Collected but unread fragment shows "New" badge; `MarkFragmentRead()` transitions it to read.
10. **Dimmed flash on exhausted pool**: When all fragments are collected, a dimmed flash appears at death location with no toast/stinger/ripple.
11. **Non-lore entity ignored**: When an entity has no `eliteTypeId`, the event is silently ignored.
12. **AddLoreFragmentAsync union-merge**: If `collectedLoreFragmentIds` already contains a fragment ID, the call is idempotent.
13. **Zone transition does not clear lore**: Collected fragment IDs survive zone transitions (persisted, not ephemeral).

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/LoreFragmentSystem/LoreFragmentServiceTests.cs`
- Collection logic (first-kill guarantee, repeat pool, exhausted)
- Persistence round-trip (union-merge, crash recovery, deduplication)
- Codex query layer (all query methods, read state)

## Dependencies

- **Event Bus** — Consumes `EntityDiedEvent`, publishes `LoreFragmentCollectedEvent`
- **Save/Profile** — `AddLoreFragmentAsync()`, `collectedLoreFragmentIds` persistence, run-state tracking

## Unlocks

- **Codex UI** — Consumes read-only query layer for fragment display

## Risks

- **LOW**: Force-quit mid-run after fragment collection grants permanent lore even though the run didn't complete. Accepted — premium single-player game with no competitive economy.
- **LOW**: New fragments added in patches cause existing players to have missing entries. Union-merge handles gracefully — new IDs are simply uncollected.
