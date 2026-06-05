# Story 003: Fault Tolerance — IOException, Network Disconnect, Synclog

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-007` | IOException: original persistent.json unchanged, error logged | ✅ ADR-006 |
| `TR-saveprofile-008` | Connected sync: server stores payload, client receives response | ✅ ADR-006 |
| `TR-saveprofile-009` | Disconnected sync: .synclog entry created | ✅ ADR-006 |
| `TR-saveprofile-010` | Synclog replay on reconnection | ✅ ADR-006 |
| `TR-saveprofile-022` | Network disconnect mid-sync: local preserved, .synclog entry | ✅ ADR-006 |
| `TR-saveprofile-025` | Synclog compaction to latest-state payload | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- ProfileSyncService owns sync orchestration — Save/Profile provides data
- `.synclog` append-only transaction log with atomic writes
- Compaction before send: merge entries into single latest-state payload
- Entry expiry uses last-attempt timestamp, not creation timestamp

## Description

Implement fault tolerance: IOException handling on disk write failures, connected vs disconnected sync behavior via ProfileSyncService, and the `.synclog` transaction log with compaction and replay.

## Design

### IOException Handling

- Catch `IOException` on file write
- Temp file write fails before any rename — original save file intact
- Log error containing "Storage full"
- Player sees non-blocking toast via Event Bus

### Connected Sync

When `INetworkManager.IsConnected`:
1. Local write completes (atomic)
2. ProfileSyncService sends payload to backend
3. Server stores payload, returns acknowledgment
4. Client receives response — sync complete

### Disconnected Sync (Synclog)

When `INetworkManager.IsConnected == false`:
1. Local write completes (atomic)
2. Sync attempt skipped
3. `.synclog` entry created with payload data
4. Entry uses atomic write pattern (`.synclog.tmp` → rename)

### Synclog Replay

On reconnect (detected via `INetworkManager.OnStateChanged`):
1. Read `.synclog` entries
2. Compact entries: merge into single latest-state payload per file path
3. Send compacted payload to server
4. On server acknowledgment, clear `.synclog`
5. On rejection (stale session): discard entry, log warning, continue

### Network Disconnect Mid-Sync

- If connection drops during server request:
  - Local `persistent.json` is already written (local-first)
  - `.synclog` entry created with the unsent payload
  - No partial server state committed

### Synclog Compaction

Before sending to server, `.synclog` entries are merged:
- Multiple sequential `PersistentSaveData` payloads → keep only the latest per file
- `.runstate` entries → keep only the latest
- Output: single `PersistentSaveData` + single `RunStateSaveData`

## Acceptance Criteria

1. **GIVEN** `IFileSystem` mock throws `IOException` on write, **WHEN** `PersistStateAsync()` is called, **THEN** original `persistent.json` is unchanged AND error contains "Storage full".
2. **GIVEN** `MockBackendService.ConnectionState == Connected` AND `PersistStateAsync()` completes locally, **WHEN** sync completes, **THEN** server mock stores the sent payload AND client receives response.
3. **GIVEN** `MockBackendService.ConnectionState == Disconnected` AND `PersistStateAsync()` completes locally, **WHEN** sync attempt fails, **THEN** `.synclog` entry exists containing the unsent data.
4. **GIVEN** `.synclog` with 1 pending entry AND `ConnectionState == Connected`, **WHEN** initialization completes, **THEN** `.synclog` entry is replayed AND server mock data matches entry AND `.synclog` is empty.
5. **GIVEN** `ConnectionState == Connected` AND `PersistStateAsync()` called, **WHEN** server request is in flight and connection drops, **THEN** local `persistent.json` is preserved AND `.synclog` entry created with unsent payload.
6. **GIVEN** `.synclog` contains 10 pending entries from sequential calls, **WHEN** the file is read before sync, **THEN** only the most recent entry per file path is retained (compacted).

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/FaultToleranceTests.cs`
- All 6 acceptance criteria as individual test methods
- Mock file system, mock backend service, mock network manager

## Dependencies

- **Save Story 001** — Core Persistence Layer (file I/O, atomic write)

## Unlocks

- None (terminal fault tolerance story)

## Risks

- **LOW**: Synclog may grow unbounded if server never acknowledges. Mitigation: compaction limits sent payload size; last-attempt expiry prevents unbounded retry.
