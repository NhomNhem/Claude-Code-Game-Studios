# Story 003: Pause Toggle & Menu Navigation

- **Epic**: Input System
- **System**: Input System
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 2h
- **Status**: Complete
- **Last Updated**: 2026-06-02
- **Manifest Version**: 2026-06-01

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-input-007` | Escape in Gameplay calls TransitionTo(Paused) | ✅ ADR-003 |
| `TR-input-008` | Escape in Paused returns to previous state | ✅ ADR-003 |
| `TR-input-009` | Menu map Enter fires focused button onClick | ✅ ADR-003 |
| `TR-input-010` | Directed-aim hold cleared on GState→Paused | ✅ ADR-003 |

## ADR Guidance

**ADR-003 (Input System & InputRouter Wrapper Pattern):**
- Pause action lives in Gameplay and Camp action maps (not Menu)
- Escape/Start toggles pause via `IGameStateManager.TransitionTo(Paused)` or `TransitionTo(previousState)`
- Menu map drives `InputSystemUIInputModule` for UI navigation
- Hold-to-aim state flushed on map disable: `SetActionMap()` iterates all held skill slots and releases any that are active, calling `UseSkill(slotIndex, lastAimDir)` to flush through the pipeline
- Losing directed-aim state on pause is documented behavior (GDD Edge Cases: "If TransitionTo(Paused) fires while a hold-to-aim skill is active")
- State reset on transition: `InputSystem.ResetDevice()` on all active devices

## Description

Wire the Pause toggle in InputRouter: Escape (KBM) / Start (gamepad) / pause button (touch) calls `IGameStateManager.TransitionTo(Paused)` or back to previous state. Integrate the Menu action map with `InputSystemUIInputModule` so Enter/Confirm fires button onClick. On pause, flush any active hold-to-aim state so no stale input bleeds into paused menus or back into gameplay.

## Design

### Pause Toggle

```csharp
public interface IPauseHandler
{
    void TogglePause();
}

public class InputRouter : IInputRouter
{
    private readonly IGameStateManager _gameStateManager;
    private GamePhase _previousPhase;

    private void OnPauseAction(InputAction.CallbackContext ctx)
    {
        if (ctx.performed)
        {
            TogglePause();
        }
    }

    private void TogglePause()
    {
        var current = _gameStateManager.CurrentPhase;

        if (current == GamePhase.InRun || current == GamePhase.BossFight || current == GamePhase.HeroCamp)
        {
            _previousPhase = current;
            _gameStateManager.TransitionTo(GamePhase.Paused);
        }
        else if (current == GamePhase.Paused)
        {
            // Return to previously stored phase (TR-input-008)
            GamePhase target = _previousPhase != GamePhase.None ? _previousPhase : GamePhase.InRun;
            _gameStateManager.TransitionTo(target);
        }
        // Silently ignored in Menu, Loading, Victory, Defeat
    }
}
```

### Hold-to-Aim Flush on Pause (TR-input-010)

When `SetActionMap()` disables the Gameplay map (or any map), flush all held skill slots:

```csharp
private void FlushHeldSkills()
{
    foreach (int slot in _heldSlots.ToList()) // copy to avoid modification during iteration
    {
        Vector2 lastDir = _lastAimDirs.GetValueOrDefault(slot, Vector2.zero);
        _characterEntity.UseSkill(slot, lastDir);
        _heldSlots.Remove(slot);
        _lastAimDirs.Remove(slot);
    }
}

public void SetActionMap(string mapName)
{
    // Before disabling current map, flush held skills
    if (IsMapWithSkills(_currentMapName))
    {
        FlushHeldSkills();
    }

    _currentMap?.Disable();
    InputSystem.ResetDevice(Mouse.current);
    InputSystem.ResetDevice(Keyboard.current);
    // ... etc for all active devices

    _currentMap = _asset.FindActionMap(mapName);
    _currentMap?.Enable();
    _currentMapName = mapName;
}
```

### UI Navigation (TR-input-009)

The Menu action map's NavigateUI, Confirm, and Back actions drive an `InputSystemUIInputModule` on the Event System. This is standard Unity Input System integration:

1. An `InputSystemUIInputModule` is attached to the Event System GameObject
2. Its `move`, `submit`, and `cancel` actions are wired to the Menu action map's `NavigateUI`, `Confirm`, and `Back` actions respectively
3. When the Menu map is enabled, UI navigation works automatically
4. When the Menu map is disabled, UI input is automatically blocked

No custom code in InputRouter is needed for the navigation itself — it's pure Unity Event System configuration. InputRouter only needs to ensure the correct action map is active for the current GState.

### VContainer Registration

```csharp
// InputRouter receives IGameStateManager via constructor injection
builder.Register<IInputRouter, InputRouter>(Lifetime.Singleton);
builder.Register<IPauseHandler>(...); // Optional: expose TogglePause for programmatic pause
```

## Acceptance Criteria

1. **Escape pauses in Gameplay**: With GState = InRun, pressing Escape calls `IGameStateManager.TransitionTo(Paused)`.
2. **Escape pauses in HeroCamp**: With GState = HeroCamp, pressing Escape calls `TransitionTo(Paused)`.
3. **Escape resumes from Paused**: With GState = Paused (entered from InRun), pressing Escape calls `TransitionTo(InRun)`.
4. **Escape silently ignored in Menu**: With GState = Menu, pressing Escape does nothing.
5. **Escape silently ignored in Victory**: With GState = Victory, pressing Escape does nothing.
6. **Directed-aim cleared on pause**: While skill slot 2 is in directed-aim hold, transitioning to Paused flushes `UseSkill(2, lastAimDir)` and clears the held state. Returning to InRun does not re-trigger the skill.
7. **Menu map Enter fires button onClick**: With Menu map active, pressing Enter fires the focused UI button's `onClick` event.
8. **UI navigation works in Menu**: With Menu map active, arrow keys/WASD navigate UI selectables.
9. **Pause in Camp**: With Camp map active, pressing Escape transitions to Paused (same as Gameplay pause).
10. **Return from Paused to correct phase**: Pausing from HeroCamp then pressing Escape returns to HeroCamp, not InRun.

## QA Test Cases

- **AC1 (Escape pauses InRun)**: Mock IGameStateManager with CurrentPhase=InRun. Fire Escape. Verify TransitionTo(Paused) called.
- **AC2 (Escape pauses HeroCamp)**: CurrentPhase=HeroCamp. Fire Escape. Verify TransitionTo(Paused) called.
- **AC3 (Escape resumes from Paused)**: CurrentPhase=Paused (_previousPhase=InRun). Fire Escape. Verify TransitionTo(InRun) called.
- **AC4 (Escape ignored in Menu)**: CurrentPhase=Menu. Fire Escape. Verify no TransitionTo call.
- **AC5 (Escape ignored in Victory)**: CurrentPhase=Victory. Fire Escape. Verify no TransitionTo call.
- **AC6 (Directed-aim cleared on pause)**: Hold slot 2, transition to Paused. Verify UseSkill(2, lastDir) called. Verify held slots empty. Verify no call on return to InRun.
- **AC7 (Menu Enter fires onClick)**: Simulate UI button focused. Fire Menu Enter. Verify onClick invoked.
- **AC8 (UI navigation works)**: Fire Menu NavigateUI down. Verify next selectable focused.
- **AC9 (Pause in Camp)**: CurrentPhase=HeroCamp. Fire Escape. Verify TransitionTo(Paused).
- **AC10 (Return to correct phase)**: Pause from HeroCamp, resume. Verify TransitionTo(HeroCamp).

**Edge cases**: _previousPhase stale on Victory-while-paused, double-press before GState transitions, null EventSystem.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/Input/PauseMenuNavTests.cs`
- Mock IGameStateManager to verify TransitionTo calls with correct phase
- Mock CharacterEntity to verify hold-to-aim flush on pause transition
- Verify held slots cleared after flush
- Verify Escape from Menu/Loading/Victory/Defeat is silently ignored

## Dependencies

- **Depends on**: Story 001 (InputRouter Core — action maps), IGameStateManager interface
- **Depends on**: Story 002 (Skill Activation — hold-to-aim state for flush on pause)
- **Unlocks**: Story 004 (Edge Cases)

## Risks

- **MEDIUM**: `_previousPhase` tracking could become stale if GState transitions happen outside pause (e.g., Victory while paused). Mitigation: update `_previousPhase` only when pausing from non-paused states; when resuming from pause, reset it to None. Consider storing the previous phase in IGameStateManager instead.
- **LOW**: InputSystemUIInputModule wiring requires scene-level configuration. Mitigation: document the required GameObject setup in the story completion notes.
