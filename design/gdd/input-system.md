# Input System

> **Status**: Designed (pending review)
> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED 2026-05-26
> **Author**: user + agents
> **Last Updated**: 2026-05-26
> **Implements Pillar**: Pillar 3 — Snappy 20–30 Minute Sessions (responsive controls)

## Overview

The Input System is the raw input routing layer. It wraps Unity's Input System 1.19.0 and translates physical input from keyboard, mouse, gamepad, and touch into game-action signals consumed by higher-layer systems. Its core responsibility is abstracting physical device events into logical game actions (Move, Aim, UseSkill, Pause, Interact) and routing them to the correct consumer via `characterEntity.Move()`, `characterEntity.UseSkill()`, and Event Bus events — without modifying template vendor code. The system respects the current game state (GState) and only routes actions valid in that state. For example, movement is only routed during `InRun`, menus are only navigable during `Menu` or `Paused`.

## Player Fantasy

The player never interacts with the Input System directly. They press keys, move sticks, and tap the screen — and the game responds instantly. The Input System's player fantasy is the absence of friction: every input maps to the expected action, every control scheme feels native (WASD moves, mouse aims, gamepad sticks steer, touch drags), and the game never misreads intent. When it works perfectly, the player doesn't notice it at all.

## Detailed Design

### Core Rules

1. **Single entry point** — `InputRouter` owns one `InputActionAsset` and wraps Unity Input System 1.19.0. All physical device input is declared in a custom `.inputactions` asset and translated into logical game actions. The template's existing `PCInputController`/`PCSkillController` are disabled when our InputRouter is active (their GameObjects deactivated in _TinyRift scenes).
2. **GState-driven map switching** — `InputRouter` subscribes to `GameStateChanged` on the Event Bus. On every transition, it calls `DisableAll()` then `Enable(mapName)` for the matching action map. Only one map is active at any time.
3. **Three action maps** — `Gameplay` (InRun), `Menu` (Menu/Paused/Victory/Defeat), `Camp` (HeroCamp). Actions from inactive maps silently no-op. `Loading` state uses no map.
4. **Move input** — reads the `Move` action (WASD/arrows on KBM, left stick on gamepad, virtual joystick on touch). Normalized `Vector2`. Each frame during InRun or HeroCamp, calls `characterEntity.Move(direction)`. Calls `characterEntity.Move(Vector3.zero)` when no input is detected to stop movement.
5. **Aim input** — reads the `Aim` action (mouse cursor on KBM, right stick on gamepad, skill joystick on touch). Computes world-space direction relative to character position. On KBM, aim always follows the mouse cursor independent of action state.
6. **Skill activation** — reads `UseSkill1–4` actions. On press (forward-aim skills): calls `characterEntity.UseSkill(slotIndex, Vector2.zero)` instantly. On press (directed-aim skills): begins piping `GetAimInput()` into `characterEntity.UpdateDirectionalAim()` each frame while held. On release: calls `characterEntity.UseSkill(slotIndex, lastAimDir)`. Preserves the template's hold-to-aim/release-to-cast contract.
7. **No manual fire** — auto-attack is fully automatic via `CharacterAttackComponent.AutoAttackLoop()`. `InputRouter` never emits a "fire" action. This is a hard template constraint.
8. **Pause toggle** — Escape (KBM), Start (gamepad), pause button (touch). Calls `IGameStateManager.TransitionTo(Paused)` if current state is InRun or HeroCamp; calls `IGameStateManager.TransitionTo(previousState)` if currently Paused. Silently ignored in Menu, Loading, Victory, Defeat.
9. **UI navigation** — `NavigateUI`, `Confirm`, and `Back` actions drive an `InputSystemUIInputModule` attached to the Event System. During Menu, Paused, Victory, or Defeat, this is the only active input path.
10. **State reset on transition** — Every action map disable is accompanied by `InputSystem.ResetDevice()` on all active devices to clear lingering press/hold state. The InputRouter holds zero state across GState transitions.

### Action Maps

| Action Map | GState(s) | Actions | KBM Bindings | Gamepad Bindings | Touch Bindings |
|-----------|-----------|---------|-------------|-----------------|---------------|
| **Gameplay** | InRun | Move, Aim, UseSkill1–4, Interact, Pause | WASD/Arrows, Mouse pos, Q/E/R/F + LMB, F, Escape | Left Stick, Right Stick, A/B/X/Y + LT/RT, A, Start | Virtual Joystick, Skill Joystick, Skill Buttons, Tap, Pause Button |
| **Menu** | Menu, Paused, Victory, Defeat | NavigateUI, Confirm, Back | Arrow/WASD, Enter/Space, Escape | D-Pad/Left Stick, A, B | Swipe/Tap, Tap, Back Swipe |
| **Camp** | HeroCamp | Move, Interact, OpenCodex, StartRun, Pause | WASD/Arrows, F, C, Enter, Escape | Left Stick, A, Y, Start, Select | Virtual Joystick, Tap, Codex Button, Start Button, Pause Button |

**Action-to-GState routing:**

| Action | Menu | HeroCamp | InRun | Paused | Victory | Defeat |
|--------|------|----------|-------|--------|---------|--------|
| Move | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Aim | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| UseSkill1–4 | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Interact | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Pause | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| NavigateUI | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Confirm | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Back | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| OpenCodex | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| StartRun | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |

### API Surface

```csharp
// Assets/_TinyRift/Runtime/Input/IInputRouter.cs
public interface IInputRouter : IDisposable
{
    // Lifecycle
    void Enable();
    void Disable();
    void SetActionMap(string mapName);

    // Polling (continuous input)
    Vector2 GetMoveInput();
    Vector2 GetAimInput();
    bool IsSkillPressed(int slotIndex);     // wasPressedThisFrame
    bool IsSkillHeld(int slotIndex);        // isPressed

    // Events (one-shot actions)
    event Action<Vector2> OnMove;
    event Action<Vector2> OnAim;
    event Action<int> OnSkillUsed;
    event Action OnPauseToggled;
    event Action OnInteract;
    event Action OnOpenCodex;
    event Action OnStartRun;
}
```

Implementation: `InputRouter` receives the `InputActionAsset` via direct reference (serialized in scene or injected via VContainer). It subscribes to `GameStateChanged` via Event Bus. Action callbacks are wired in `Awake()` using `action.performed += Handler` pattern. `SetActionMap()` calls `currentMap?.Disable()`, then `asset.FindActionMap(mapName)?.Enable()`.

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| Game State Manager | Subscribes to `GameStateChanged` event | GState → Input | State enum (GState) → triggers map switch |
| CharacterEntity (template) | Calls `Move()`, `UseSkill()`, `UpdateDirectionalAim()` | Input → Character | Vector2 moveDir, int skillIdx + Vector2 aimDir |
| Event Bus | Publishes `OnInteract`, `OnOpenCodex`, `OnStartRun` | Input → Event Bus | Action event (struct) |
| UI Event System | `NavigateUI`, `Confirm`, `Back` drive `InputSystemUIInputModule` | Input → UI | Vector2 navigation, confirm/back signals |
| Pause (via GState) | Calls `GameStateManager.TransitionTo(Paused)` | Input → GState | Target state |
| Save/Profile (future) | Reads/writes rebinding overrides via PlayerPrefs | Input ↔ Save | JSON binding override string |
| HUD (future) | Reads current input device type to show correct button prompts | Input → HUD | DeviceType enum (KBM/Gamepad/Touch) |

## Formulas

None. The Input System is a routing layer with no mathematical calculations. All output values are normalized `Vector2` from Unity Input System controls or boolean press/release signals.

## Edge Cases

- **If KBM and gamepad are simultaneously connected and both produce Aim input**: InputRouter detects the dominant input device for the current frame. On KBM, mouse always dominates; on gamepad, right-stick dominates. Detection via first non-zero aim source each frame.
- **If `UseSkill` index exceeds `characterData.skills.Length`**: InputRouter guards with `CharacterEntity.GetSkillCount()` before routing. If `slotIndex >= skillCount`, the press is silently dropped.
- **If the rebinding override save is corrupted**: Wrap the load in try/catch. On failure, log error and fall back to default bindings. Expose `ResetBindingsToDefaults()`.
- **If a device is disconnected mid-hold-to-aim**: Subscribe to `InputSystem.onDeviceChange` with `InputDeviceChange.Removed`. When the device providing an active hold-to-aim skill is removed, immediately release the skill by calling `UseSkill(slotIndex, lastKnownDir)` and clearing the held state.
- **If `TransitionTo(Paused)` fires while a hold-to-aim skill is active**: `SetActionMap()` iterates all held skill slots and releases any that are active, calling `UseSkill(slotIndex, lastAimDir)` to flush through the pipeline.
- **If non-zero Move input arrives on the same frame GState transitions away from InRun**: On `SetActionMap()` (disable previous map), call `characterEntity.Move(Vector3.zero)` and `characterEntity.UpdateDirectionalAim(Vector2.zero)` to flush movement before the map is disabled.
- **If Escape is rebound to Enter (shared with UI Confirm)**: After rebinding, pressing Enter in a menu fires both Confirm and a Pause attempt. GState silently rejects TransitionTo(Paused) from Menu, but the double-binding is confusing. InputRouter warns during rebinding if a binding conflicts with UI action paths.
- **If Loading → InRun transition completes before `GameStateChanged` is received**: Event bus dispatch order must fire `GameStateChanged(Loading, InRun)` before `SceneManager` marks the scene active, so InputRouter enables the Gameplay map before auto-attack resumes.
- **If focus loss auto-pause clears held keys (player alt-tabs)**: `InputSystem.ResetDevice()` clears all held keys. Acceptable constraint: player must re-press W after returning. Documented behavior, not a bug.

## Dependencies

| System | Dependency | Direction | Notes |
|--------|-----------|-----------|-------|
| Unity Input System 1.19.0 | Required | InputRouter → Package | Runtime dependency for all input |
| Game State Manager | Required | GState → Input | Subscribes to `GameStateChanged` for map switching |
| CharacterEntity (template) | Required | InputRouter → Character | Calls Move(), UseSkill(), UpdateDirectionalAim() |
| Event Bus | Required | InputRouter → Event Bus | Publishes OnInteract, OnOpenCodex, OnStartRun |
| VContainer | Required | TinyRiftScope → Input | Registers IInputRouter as singleton |
| UI Event System | Required | InputRouter → UI | NavigateUI/Confirm/Back drive InputSystemUIInputModule |
| Save/Profile (future) | Optional | Input ↔ Save | Saves/loads rebinding overrides as JSON |

## Tuning Knobs

| Knob | Type | Default | Range | Notes |
|------|------|---------|-------|-------|
| Inner dead zone (gamepad left stick) | float | 0.15 | 0.0–0.5 | Applies to Move action processor |
| Outer dead zone (gamepad left stick) | float | 0.95 | 0.8–1.0 | Applies to Move action processor |
| Inner dead zone (gamepad right stick) | float | 0.20 | 0.0–0.5 | Higher default to prevent drift |
| Touch joystick max radius | int (px) | 60 | 30–120 | Virtual joystick drag distance |
| Key rebinding overrides | JSON string | empty | — | Saved per-user via PlayerPrefs |
| Active action map | string enum | "Menu" | Gameplay/Menu/Camp | Switched by GState, not user-configurable |

## Visual/Audio Requirements

None. The Input System is invisible to the player. All visual feedback (crosshair, direction indicators, button prompts) and audio feedback (UI click SFX, combat SFX) belong to the systems that consume input events, not to the Input System itself.

## UI Requirements

None for the Input Router itself. The rebinding settings screen (Settings → Controls) will consume `InputActionRebindingExtensions` at implementation time but is a UI system concern, not an Input System concern. MVP uses default bindings only.

## Open Questions

1. Should auto-switch detection (KBM vs gamepad dominant device) live in InputRouter or a separate `IDeviceDetector` service?
   → **Recommendation**: Lightweight detection in InputRouter (check `InputSystem.devices` and last-input tracking). Extract to separate service if logic grows. Resolved during implementation.
2. Gamepad rebinding UI: deferred to Vertical Slice. MVP uses default gamepad bindings only.
3. Aim assist: deferred to post-MVP. No aim assist logic in the base Input System GDD.

## Acceptance Criteria

- **GIVEN** GState transitions from Gameplay to Menu, **WHEN** the transition completes, **THEN** InputRouter switches to the Menu action map.
- **GIVEN** the Gameplay map is active, **WHEN** the player holds W, **THEN** `characterEntity.Move(Vector2(0,1))` is called every frame.
- **GIVEN** Move was called last frame, **WHEN** the player releases all movement keys, **THEN** `characterEntity.Move(Vector2(0,0))` is called.
- **GIVEN** the Gameplay map is active, **WHEN** the mouse cursor is at a position relative to the character, **THEN** `characterEntity.UpdateDirectionalAim()` is called with the normalized direction.
- **GIVEN** the player presses skill slot 1 (forward-aim), **WHEN** the press occurs, **THEN** `characterEntity.UseSkill(1, Vector2.zero)` is called exactly once.
- **GIVEN** the player presses and holds skill slot 2 (directed-aim) for 400ms, **WHEN** the release occurs, **THEN** `characterEntity.UseSkill(2, lastAimDir)` is called exactly once with the last known aim direction.
- **GIVEN** GState is Gameplay, **WHEN** the player presses Escape, **THEN** `TransitionTo(Paused)` is called.
- **GIVEN** GState is Paused, **WHEN** the player presses Escape, **THEN** GState returns to the previous state.
- **GIVEN** the Menu map is active, **WHEN** the player presses Enter/Confirm, **THEN** the focused button's onClick fires.
- **GIVEN** skill slot 3 is in directed-aim hold state, **WHEN** GState transitions to Paused, **THEN** the held state is cleared and `UseSkill` is NOT called on return.
- **GIVEN** the player rebinds MoveUp from W to UpArrow, **WHEN** the game saves and reloads, **THEN** pressing UpArrow moves the character forward.
- **GIVEN** PlayerPrefs contains corrupted JSON, **WHEN** the game loads rebinds, **THEN** no exception is thrown and default bindings remain active.
- **GIVEN** skill slot 2 is in directed-aim hold state, **WHEN** the input device disconnects, **THEN** the held state is cleared and `UseSkill` is not called.
- **GIVEN** the Gameplay map is active, **WHEN** the player presses skill slot 5 (out of range), **THEN** no call is made to `UseSkill`.
- **GIVEN** skill slot 2 is in directed-aim hold state, **WHEN** the player presses skill slot 1 (forward-aim), **THEN** `UseSkill(1, Vector2.zero)` fires normally.
- **GIVEN** GState transitions from Gameplay to Menu while the player is holding W, **WHEN** the Menu map activates, **THEN** `characterEntity.Move` is not called during Menu and input is cleanly reacquired on return.
