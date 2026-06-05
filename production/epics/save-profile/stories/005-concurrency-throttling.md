# Story 005: Concurrency & Throttling — Debounce, Coalescing

- **Epic**: Save & Profile
- **System**: Save/Profile Persistence
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-saveprofile-017` | Same-frame calls produce exactly one disk write | ✅ ADR-006 |
| `TR-saveprofile-018` | 60 calls debounced to one disk write | ✅ ADR-006 |
| `TR-saveprofile-023` | Concurrent read during write returns pre-write state | ✅ ADR-006 |

## ADR Guidance

**ADR-006 (Save/Profile Serialization):**
- Dirty-flag + debounce write coalescing
- Write semaphore protects disk I/O; dirty-flag layer above provides coalescing
- Settings writes have additional 500ms debounce for slider-drag thrashing

## Description

Implement write coalescing via dirty-flag + debounce pattern. Multiple rapid `PersistStateAsync()` calls produce exactly one disk write. Concurrent reads during an active write return pre-write state.

## Design

### Dirty-Flag + Debounce

```csharp
private bool _dirty;
private PersistentSaveData _pendingSnapshot;
private CancellationTokenSource _debounceCts;

public async UniTask PersistStateAsync()
{
    _pendingSnapshot = CaptureSnapshot();
    _dirty = true;

    if (_writeCts == null || _writeCts.IsCancellationRequested)
    {
        _writeCts = new CancellationTokenSource();
        await DebounceAndWrite(_writeCts.Token);
    }
}

private async UniTask DebounceAndWrite(CancellationToken ct)
{
    await UniTask.Delay(100, cancellationToken: ct);

    if (!_dirty) return;

    _dirty = false;
    var snapshot = _pendingSnapshot;

    await _writeSemaphore.WaitAsync();
    try
    {
        await AtomicWriteAsync(snapshot);
    }
    finally
    {
        _writeSemaphore.Release();
    }
}
```

- `PersistStateAsync()` captures snapshot, sets dirty flag, returns immediately
- If no write loop active, starts one with debounce timer (default 100ms)
- If write loop already running, new calls update `_pendingSnapshot` only
- When debounce fires, writes latest snapshot to disk exactly once

### Settings Debounce

- `ApplySettingsAsync()` uses additional 500ms debounce specific to settings
- Prevents slider-drag thrashing during UI adjustment
- Same underlying mechanism with longer delay

### Concurrent Read During Write

- `_writeSemaphore` protects disk I/O
- `LoadPersistentAsync()` checks if write semaphore is acquired
- If write in progress: read returns the pre-write state (read from disk before write starts, or return cached pre-write snapshot)
- Write semaphore released only after disk write completes

### Same-Frame Coalescing

- 60 calls in one frame → dirty flag set once per call, one debounce fires
- Final disk write reflects latest `_pendingSnapshot`
- No intermediate values appear on disk

## Acceptance Criteria

1. **GIVEN** two `PersistStateAsync()` calls in the same synchronous execution slice, **WHEN** both return, **THEN** exactly one disk write occurs AND written data reflects the second caller's snapshot (latest wins).
2. **GIVEN** 60 `PersistStateAsync()` calls in rapid succession (within one frame), **WHEN** debounce timer fires after 100ms, **THEN** exactly one disk write occurs AND `persistent.json.gold` equals the last call's value AND no intermediate values appear.
3. **GIVEN** `PersistStateAsync()` is in progress (semaphore acquired), **WHEN** `LoadPersistentAsync()` is called, **THEN** the read returns the pre-write state until write completes AND semaphore is released.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/SaveProfile/ConcurrencyThrottlingTests.cs`
- All 3 acceptance criteria as individual test methods
- Timing-dependent tests use virtual time or manual debounce triggering
- Verify exactly-once write via write-counter on mock file system

## Dependencies

- **Save Story 001** — Core Persistence Layer (atomic write, snapshot capture)

## Unlocks

- None (standalone throttling)

## Risks

- **LOW**: Debounce timer may delay writes during scene transitions. Mitigation: default 100ms is imperceptible; settings 500ms is acceptable for slider operations.
