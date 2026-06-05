# Story 004: Conflict Resolution — Scalar, List, Quarantine

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Integration
- **Priority**: P1
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-013` | Scalar currency conflict: newer lastModified wins | ✅ ADR-006 |
| `TR-saveprofile-014` | List union-merge: no duplicates | ✅ ADR-006 |
| `TR-saveprofile-015` | Server quarantine: overwrite local, no retry | ✅ ADR-006 |
| `TR-saveprofile-016` | Reward notification: non-blocking toast | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- Per-field `lastModified` timestamps for scalar conflict resolution
- Union-merge for progression lists (monotonic append-only)
- Server quarantine returns authoritative snapshot, no client retry

**Control Manifest (Core Layer):**
- ProfileSyncService orchestrates conflict resolution
- Reward notification is non-blocking toast (no modal)

## Description

Implement conflict resolution strategies for sync scenarios: scalar currency fields use newest-`lastModified` wins, progression lists use union-merge, and server quarantine overwrites local state. Reward notification fires on offline-earned progress.

## Design

### Scalar Currency Resolution

```csharp
if (local.lastModified > server.lastModified)
    useLocalValue();
else if (server.lastModified > local.lastModified)
    useServerValue();
else
    useTiebreaker(); // device-ID lexicographic order
```

- Per-field `lastModified` Unix ms timestamps
- Server validates: rejects timestamps newer than server time, rejects timestamps <= `lastAcceptedTimestamp` per field per player (replay protection)

### List Union-Merge

```csharp
mergedList = localList.Union(serverList).ToList();
```

- Applied to: `unlockedHeroIds`, `unlockedZoneIds`, `collectedLoreFragmentIds`
- Once unlocked, never removed by sync conflict
- Order: local order preserved, new server items appended
- No duplicates

### Server Quarantine

When server detects fraud (balance exceeds `maxBalanceGold`):
1. Server returns authoritative snapshot
2. Client overwrites local `persistent.json` with server data
3. No retry attempted
4. No reward notification toast (suppressed)
5. Non-blocking notification: "Your balance was adjusted to match the server. Contact support if you believe this is an error."

### Reward Notification

On offline reward receipt:
- `RewardNotificationService` receives `OfflineRewardData`
- Gold counter animates from pre-sync value to pre-sync + amount
- Non-blocking toast appears (e.g., "Earned while away: +500g")
- No modal, no OK/Claim button
- Toast auto-dismisses after timeout (default 30s)

## Acceptance Criteria

1. **GIVEN** local `gold = 1000` with `goldLastModified = T1` AND server `gold = 500` with `goldLastModified = T2` AND `T1 > T2`, **WHEN** sync completes, **THEN** server stores `gold = 1000` AND `goldLastModified = T1`.
2. **GIVEN** local `gold = 500` with `goldLastModified = T1` AND server `gold = 1000` with `goldLastModified = T2` AND `T2 > T1`, **WHEN** sync completes, **THEN** local `gold` becomes `1000` AND `goldLastModified` becomes `T2`.
3. **GIVEN** local `unlockedHeroIds = ["warrior", "mage"]` AND server `unlockedHeroIds = ["warrior", "rogue"]`, **WHEN** sync completes, **THEN** both sides contain `["warrior", "mage", "rogue"]` (union, no duplicates).
4. **GIVEN** server quarantines a sync payload, **WHEN** sync response is received, **THEN** local `gold` is overwritten with server value AND no retry is attempted AND no reward toast is shown.
5. **GIVEN** `RewardNotificationService` receives `OfflineRewardData` with `gold = 500`, **WHEN** sync completes, **THEN** `ReceivedRewards` contains `{ currency: "gold", amount: 500 }`.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/ConflictResolutionTests.cs`
- All 5 acceptance criteria as individual test methods
- Mock server for quarantine scenario

## Dependencies

- **Save Story 001** — Core Persistence Layer (data model, file I/O)

## Unlocks

- None (standalone conflict resolution)

## Risks

- **LOW**: Clock skew between devices may cause incorrect `lastModified` ordering. Mitigation: server validates timestamps against its own clock.
