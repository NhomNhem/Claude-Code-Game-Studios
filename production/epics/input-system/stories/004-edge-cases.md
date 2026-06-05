# Story 004: Edge Cases — Device Disconnect, Rebinds, State Safety

- **Epic**: Input System
- **System**: Input System
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-02

## Completion Notes
**Completed**: 2026-06-02
**Criteria**: 7/7 passing
**Deviations**: None
**Test Evidence**: Logic: test file at Assets/_TinyRift/Tests/EditMode/Input/EdgeCaseTests.cs
**Code Review**: Complete (Approved with Suggestions)

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-input-011` | Rebinding persists across restart | ✅ ADR-003 |
| `TR-input-012` | Corrupted PlayerPrefs loads defaults | ✅ ADR-003 |
| `TR-input-013` | Device disconnect clears held state | ✅ ADR-003 |

## ADR Guidance

**ADR-003 (Input System & InputRouter Wrapper Pattern):**
- Rebinding uses `InputActionRebindingExtensions.SaveBindingOverridesAsJson()` / `LoadBindingOverridesFromJson()`
- Corrupted save: wrap load in try/catch, log error, fall back to default bindings
- Device disconnect: subscribe to `InputSystem.onDeviceChange` with `InputDeviceChange.Removed`
- When the device providing an active hold-to-aim skill is removed, immediately release the skill by calling `UseSkill(slotIndex, lastKnownDir)` and clearing held state
- Expose `ResetBindingsToDefaults()` API
- Rebinding overrides saved to PlayerPrefs per-user as JSON string

## Description

Implement edge case resilience for InputRouter: (1) rebinding persistence via PlayerPrefs with JSON serialization and corrupted-data fallback, (2) device disconnect handling that releases active hold-to-aim skills cleanly, and (3) API surface for resetting bindings to defaults. These hardening measures ensure the Input System is safe against real-world failure modes.

## Design

### Rebinding Persistence (TR-input-011, TR-input-012)

```csharp
public class InputRouter : IInputRouter
{
    private const string RebindsPlayerPrefsKey = "InputBindingOverrides";

    public void SaveBindings()
    {
        string json = _asset.SaveBindingOverridesAsJson();
        PlayerPrefs.SetString(RebindsPlayerPrefsKey, json);
        PlayerPrefs.Save();
    }

    public void LoadBindings()
    {
        try
        {
            string json = PlayerPrefs.GetString(RebindsPlayerPrefsKey, null);
            if (!string.IsNullOrEmpty(json))
            {
                _asset.LoadBindingOverridesFromJson(json);
            }
            // If null/empty: default bindings remain (first launch)
        }
        catch (Exception ex)
        {
            // TR-input-012: corrupted data -> log and fall back to defaults
            Debug.LogError($"Failed to load binding overrides: {ex.Message}. Falling back to defaults.");
            ResetBindingsToDefaults();
        }
    }

    public void ResetBindingsToDefaults()
    {
        _asset.RemoveAllBindingOverrides();
        PlayerPrefs.DeleteKey(RebindsPlayerPrefsKey);
        PlayerPrefs.Save();
    }

    public string GetBindingJsonForDisplay()
    {
        return _asset.SaveBindingOverridesAsJson();
    }
}
```

### Device Disconnect (TR-input-013)

```csharp
public class InputRouter : IInputRouter, IDisposable
{
    public InputRouter(/* ... */)
    {
        InputSystem.onDeviceChange += OnDeviceChanged;
    }

    private void OnDeviceChanged(InputDevice device, InputDeviceChange change)
    {
        if (change == InputDeviceChange.Removed && HasActiveHoldFromDevice(device))
        {
            // Release all held skills that were using this device
            FlushHeldSkillsForDevice(device);
        }
    }

    private bool HasActiveHoldFromDevice(InputDevice device)
    {
        // Check if _heldSlots has any entries driven by the disconnected device
        // For simplicity: if any slot is held and the device was the last input source,
        // release that slot. KBM disconnect is rare; gamepad disconnect is more common.
        return _heldSlots.Count > 0;
    }

    private void FlushHeldSkillsForDevice(InputDevice device)
    {
        foreach (int slot in _heldSlots.ToList())
        {
            Vector2 lastDir = _lastAimDirs.GetValueOrDefault(slot, Vector2.zero);
            _characterEntity.UseSkill(slot, lastDir);
            _heldSlots.Remove(slot);
            _lastAimDirs.Remove(slot);
        }
        Debug.Log($"InputRouter: Released held skills after device disconnect ({device.displayName})");
    }

    public void Dispose()
    {
        InputSystem.onDeviceChange -= OnDeviceChanged;
    }
}
```

### API Surface Additions

```csharp
public interface IInputRouter : IDisposable
{
    // Existing members...

    // Rebinding (added in this story)
    void SaveBindings();
    void LoadBindings();
    void ResetBindingsToDefaults();
    string GetBindingJsonForDisplay();
}
```

### Edge Case: Double-Disconnect

If `Dispose()` is called while devices are connected, `InputSystem.onDeviceChange` is unsubscribed. If a device then disconnects, no handler fires — but since InputRouter is disposed, no held state exists. Safe.

### Edge Case: Reconnect

When a device reconnects (InputDeviceChange.Added), no special handling is needed. InputRouter will pick up input from the reconnected device naturally. Held state was already flushed on disconnect, so there's no stale state to manage.

## Acceptance Criteria

1. **Rebind persists**: Player rebinds MoveUp from W to UpArrow, calls SaveBindings(), restarts the app, calls LoadBindings() — pressing UpArrow moves the character forward.
2. **Corrupted rebind data**: PlayerPrefs contains corrupted JSON (e.g., `"{broken"`), LoadBindings() catches the exception, logs an error, and default bindings remain active.
3. **Missing rebind data**: PlayerPrefs has no rebind key, LoadBindings() leaves default bindings active.
4. **Device disconnect releases hold**: Skill slot 2 is in directed-aim hold, keyboard disconnects, the held state is cleared and `UseSkill(2, lastDir)` is called. The skill fires with the last known aim direction.
5. **Device disconnect no-op when idle**: No skills held, a device disconnects — no crash, no exception.
6. **ResetBindingsToDefaults**: After calling ResetBindingsToDefaults(), all binding overrides are removed and PlayerPrefs key is deleted.
7. **Dispose unsubscribes**: After Dispose(), device disconnect does not call any InputRouter method.

## QA Test Cases

- **AC1 (Rebind persists)**: Rebind W→UpArrow. SaveBindings(). LoadBindings() in new session. Verify pressing UpArrow produces Move(Vector2(0,1)).
- **AC2 (Corrupted JSON)**: Set PlayerPrefs key to "{broken". Verify LoadBindings() catches exception, logs error, default bindings active.
- **AC3 (Missing rebind data)**: No PlayerPrefs key. Verify LoadBindings() leaves defaults active.
- **AC4 (Device disconnect releases hold)**: Hold slot 2. Simulate InputDeviceChange.Removed for active device. Verify UseSkill(2, lastDir) called, held state cleared.
- **AC5 (Device disconnect idle)**: No held skills. Simulate device disconnect. Verify no exception.
- **AC6 (ResetBindingsToDefaults)**: After custom rebind, call ResetBindingsToDefaults(). Verify all overrides removed and PlayerPrefs key deleted.
- **AC7 (Dispose unsubscribes)**: Call Dispose(). Simulate device disconnect. Verify no InputRouter method called.

**Edge cases**: Double-disconnect, reconnect after disconnect (no stale state), PlayerPrefs key collision.

**Note**: PlayerPrefs in EditMode tests — wrap IStorageProvider interface for testability, or clean up keys in [TearDown].

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/Input/EdgeCaseTests.cs`
- Mock PlayerPrefs via helper layer for testability (or use direct PlayerPrefs manipulation in EditMode tests with cleanup)
- Simulate corrupted JSON string to verify try/catch fallback
- Use `InputSystemTestFixture` or simulate device change events
- Verify `ResetBindingsToDefaults()` clears state and deletes key
- Verify `Dispose()` unsubscribes from device change events

## Dependencies

- **Depends on**: Story 002 (Skill Activation — hold-to-aim state for device disconnect flush)
- **Depends on**: Story 003 (Hold-to-aim flush pattern — reused for device disconnect)
- **Unlocks**: None

## Risks

- **MEDIUM**: PlayerPrefs in EditMode tests persists across test runs. Mitigation: wrap PlayerPrefs in an `IStorageProvider` interface for testability, or delete keys in `[TearDown]`.
- **LOW**: Device disconnect simulation requires Unity Input System testing utilities. Mitigation: extract device-detection logic into a testable helper or use `InputSystemTestFixture` from the Input System package.
- **LOW**: Rebinding UI is deferred to a future story (UX/UI epic not yet planned). This story only provides the persistence API — no UI screen is built here.
