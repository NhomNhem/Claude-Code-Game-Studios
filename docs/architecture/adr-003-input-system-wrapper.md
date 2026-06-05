# ADR-003: Input System & InputRouter Wrapper Pattern

## Status

Accepted

## Date

2026-06-01

## Decision Makers

user + agents (technical-director, unity-specialist, architecture-decision skill)

## Summary

Wrap Unity Input System 1.19.0 in a custom `InputRouter` service that abstracts three device types (KBM, gamepad, touch) into logical game actions, switches action maps by GState via Event Bus subscription, and exposes a clean `IInputRouter` interface for the rest of the game. Never uses legacy Input or template input controllers.

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Input |
| **Knowledge Risk** | HIGH — Input System 1.19.0 is post-LLM-cutoff. Legacy Input deprecated in Unity 6. |
| **References Consulted** | `docs/engine-reference/unity/modules/input.md` (full API reference), `docs/engine-reference/unity/breaking-changes.md` (Input deprecation), `docs/engine-reference/unity/deprecated-apis.md` (Input migration table) |
| **Post-Cutoff APIs Used** | `InputActionAsset`, `InputActionMap`, `InputAction.performed`, `InputSystem.onDeviceChange`, `EnhancedTouchSupport`, `SaveBindingOverridesAsJson` — all confirmed in engine reference docs |
| **Verification Required** | Test all three device types on target platforms. Verify touch EnhancedTouch works on mobile. Verify `InputSystem.ResetDevice()` clears all held state on map switch. |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (TinyRiftScope registration in Foundation layer), ADR-002 (Event Bus for GState subscription + action event publishing) |
| **Enables** | ADR-004 (Time System — pause maps to GState via input), all Feature systems that consume input (Orbit/Burst Skill, Draft Panel, Camp Menu) |
| **Blocks** | None directly — systems can stub input during development. But no Feature system works without input in a build. |
| **Ordering Note** | Must be implemented after ADR-002 (Event Bus exists to receive GameStateChangedEvent) and after a custom `.inputactions` asset is created in `Assets/_TinyRift/`. |

## Context

### Problem Statement

The template ships with `PCInputController` / `PCSkillController` that drive its own character and skill systems. Our custom code needs its own input routing that: (a) never touches template controllers, (b) respects GState (no move input during menus), (c) supports three device types uniformly, and (d) exposes a clean interface for the rest of the game. Unity Input System 1.19.0 is HIGH risk due to post-cutoff API changes — we must verify all APIs against engine reference docs, not rely on training data.

### Current State

- Unity Input System 1.19.0 package is installed (template dependency)
- Template uses `PCInputController`/`PCSkillController` in its scenes — our scenes disable these
- No custom `.inputactions` asset for TinyRift
- No `IInputRouter` implementation exists
- Architecture doc lists Input under Foundation (order-independent)

### Constraints

- **Legacy Input banned**: `Input.GetKey`, `Input.GetMouseButton`, `Input.GetAxis` must never appear in custom code
- **Template boundary**: Must not modify or reference template input controllers. Template's `CharacterEntity` template methods (`Move()`, `UseSkill()`) are called via interface, not by changing template code
- **GState fidelity**: Movement input must only flow during `InRun`/`HeroCamp`. Skill input only during `InRun`. UI navigation only during `Menu`/`Paused`/`Victory`/`Defeat`
- **Three device types**: KBM, gamepad, touch — must all work without per-device branching in consumers
- **AOT safety**: `InputAction.CallbackContext` is a struct — safe under IL2CPP. No generic delegate issues

### Requirements

- Zero legacy `Input` class calls in `Assets/_TinyRift/`
- InputRouter switches action maps within 1 frame of GState change
- Movement input delivered every frame during active GState (polling)
- Skill activation delivered as events (one-shot)
- UI navigation driven by `InputSystemUIInputModule` (standard Unity pattern)
- Device auto-detection (KBM vs gamepad) for future button prompt display
- Rebinding saved as JSON via `SaveBindingOverridesAsJson()` — deferred to post-MVP

## Decision

Use a custom `InputRouter` class implementing `IInputRouter` that wraps an `InputActionAsset` directly (no generated C# class, no `PlayerInput` component). Three action maps (`Gameplay`, `Menu`, `Camp`) switched by GState via Event Bus. Continuous input exposed as polling methods (`GetMoveInput()`), one-shot actions exposed as C# events (`OnPauseToggled`).

### Architecture

```
                    InputActionAsset (.inputactions)
                    ├── Gameplay map (InRun)
                    │   ├── Move (Value Vector2) — KBM WASD, gamepad L-stick, touch V-joystick
                    │   ├── Aim (Value Vector2) — Mouse pos, gamepad R-stick, touch skill-joystick
                    │   ├── UseSkill1..4 (Button) — Q/E/R/F + LMB, A/B/X/Y + LT/RT, skill buttons
                    │   ├── Interact (Button) — F, A, tap
                    │   ├── Pause (Button) — Escape, Start, pause button
                    │   └── NavigateUI, Confirm, Back (via InputSystemUIInputModule)
                    ├── Menu map (Menu/Paused/Victory/Defeat)
                    │   └── NavigateUI, Confirm, Back (via InputSystemUIInputModule)
                    └── Camp map (HeroCamp)
                        ├── Move (Value Vector2) — same as Gameplay
                        ├── Interact (Button)
                        ├── OpenCodex (Button)
                        ├── StartRun (Button)
                        ├── Pause (Button)
                        └── NavigateUI, Confirm, Back

                              InputRouter (IInputRouter)
                              ├── Owns InputActionAsset reference (serialized or resolved)
                              ├── Subscribes to GameStateChangedEvent (Event Bus)
                              │   └── On change: DisableAll() → Enable(newMap) → ResetDevice()
                              ├── Polling (called by CharacterEntity each frame):
                              │   ├── GetMoveInput() → ReadValue<Vector2>() from Gameplay.Move
                              │   └── GetAimInput() → ReadValue<Vector2>() from Gameplay.Aim
                              ├── Events (one-shot, wired in Awake):
                              │   ├── OnSkillUsed(slot) — UseSkill1..4 performed
                              │   ├── OnPauseToggled — Pause performed
                              │   ├── OnInteract — Interact performed (publishes to Event Bus)
                              │   ├── OnOpenCodex — OpenCodex performed
                              │   └── OnStartRun — StartRun performed
                              └── Device detection:
                                  └── Tracks last active device type from callback context.control.device

                    Consumers
                    ├── CharacterEntity (template) — receives Move() + UseSkill() calls
                    ├── Event Bus — receives Interact, OpenCodex, StartRun events as structs
                    ├── Game State Manager — receives Pause toggles via IGameStateManager
                    └── UI Event System — receives NavigateUI/Confirm/Back via InputSystemUIInputModule
```

### Key Interfaces

```csharp
public interface IInputRouter : IDisposable
{
    void Enable();
    void Disable();
    void SetActionMap(string mapName);

    // Polling (called every frame by consumers)
    Vector2 GetMoveInput();
    Vector2 GetAimInput();
    bool IsSkillPressed(int slotIndex);
    bool IsSkillHeld(int slotIndex);

    // Events (wired in InputRouter.Awake from InputAction.performed)
    event Action<int> OnSkillUsed;
    event Action OnPauseToggled;
    event Action OnInteract;
    event Action OnOpenCodex;
    event Action OnStartRun;
}
```

### Implementation Guidelines

1. **InputActionAsset reference**: Serialized as a `[SerializeField] private InputActionAsset _inputAsset` on the `InputRouter` MonoBehaviour. The `.inputactions` asset lives in `Assets/_TinyRift/Resources/Input/`.

2. **Map switching**: On `GameStateChangedEvent`:
   ```csharp
   private void OnGameStateChanged(GameStateChangedEvent evt)
   {
       SetActionMap(evt.Current switch
       {
           GameState.InRun => "Gameplay",
           GameState.HeroCamp => "Camp",
           _ => "Menu" // Menu, Paused, Victory, Defeat all use Menu map
       });
       InputSystem.ResetDevice(Keyboard.current);
       InputSystem.ResetDevice(Gamepad.current);
       // Touch reset is implicit — no held state across scenes
   }
   ```

3. **Device detection**: Track last active device type in a private field. On each action callback, check `ctx.control.device`:
   ```csharp
   private InputDeviceType _lastDevice;
   private void OnActionPerformed(InputAction.CallbackContext ctx)
   {
       _lastDevice = ctx.control.device switch
       {
           Keyboard or Mouse => InputDeviceType.KeyboardMouse,
           Gamepad => InputDeviceType.Gamepad,
           Touchscreen => InputDeviceType.Touch,
           _ => _lastDevice
       };
   }
   ```

4. **Hold-to-aim skill**: On `UseSkill` performed with a directed-aim skill, set a state flag. On `canceled` (release), route `UseSkill(slot, lastAimDir)`. On map disable, flush all held skills with `UseSkill(slot, lastAimDir)` before disabling.

5. **Rebinding**: Deferred to post-MVP. Use `SaveBindingOverridesAsJson()` / `LoadBindingOverridesFromJson()` with PlayerPrefs storage. The `IInputRouter` interface exposes `RebindAction(string actionName)` and `ResetBindingsToDefaults()` stubs.

6. **Touch**: Enable `EnhancedTouchSupport` in `InputRouter.Awake()`. The `.inputactions` asset includes touch bindings in all three maps.

7. **VContainer registration**: Registered in TinyRiftScope Foundation layer:
   ```csharp
   private void ConfigureFoundation(IContainerBuilder builder)
   {
       builder.RegisterComponentInHierarchy<InputRouter>().As<IInputRouter>();
       // InputRouter is a MonoBehaviour placed on the TinyRiftScope GameObject
       // or a dedicated Input GameObject in the startup scene
   }
   ```

## Alternatives Considered

### Alternative 1: Generated C# class from .inputactions

- **Description**: Unity can auto-generate a C# class from the `.inputactions` asset (check "Generate C# Class" in Inspector). This gives strongly-typed access to all action maps and their actions.
- **Pros**: Compile-time safety for action names, no string-based Lookup calls.
- **Cons**: Tight coupling to Unity code generation pipeline. Generated file must be re-generated when .inputactions changes. Cannot easily swap or mock at test time without wrapping (which brings us back to the wrapper pattern).
- **Rejection Reason**: We'd need a wrapper anyway for testability and GState switching. The generated class adds an intermediate step without eliminating the wrapper.

### Alternative 2: Unity PlayerInput component

- **Description**: Use the `PlayerInput` component with "Invoke C# Events" behavior. Each action maps to a UnityEvent in the Inspector.
- **Pros**: Zero code for basic setup, visual mapping in Inspector.
- **Cons**: Events are `UnityEvent` (heavy, reflection-based). Cannot easily support GState-driven map switching without custom code. Template-like coupling — the component is designed for simple games, not layered architecture.
- **Rejection Reason**: Too template-coupled and heavyweight for a Foundation service that needs interface-based DI.

### Alternative 3: Legacy Input (direct device polling)

- **Description**: Use the deprecated `Input.GetKey`, `Input.GetMouseButton`, etc. directly without any wrapper.
- **Pros**: Familiar, no setup required.
- **Cons**: Deprecated in Unity 6. No gamepad support without XInput wrappers. No touch support. No rebinding. No action abstraction.
- **Rejection Reason**: Banned by engine compatibility rules. Would fail any code review.

## Consequences

### Positive

- Clean abstraction over three device types — consumers never know which device produced input
- GState-driven map switching guarantees input fidelity without per-system checks
- Template controllers (`PCInputController`/`PCSkillController`) are disabled in our scenes — zero conflict
- `IInputRouter` interface enables unit testing by mock injection
- Rebinding deferred to post-MVP without interface changes
- Device detection ready for button prompt display (future HUD work)

### Negative

- Requires manual `InputActionAsset` setup and serialization — more boilerplate than generated class
- Hold-to-aim state tracking adds internal complexity to InputRouter
- `RegisterComponentInHierarchy` means InputRouter must exist in the startup scene — cannot be purely code-created
- Touch EnhancedTouch must be enabled manually in Awake

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Post-cutoff API change in Input System 1.19.0 | Low | Medium — action map API stable for years | All APIs verified against `docs/engine-reference/unity/modules/input.md` |
| Template input controllers conflict with ours | High | Low — template controllers disabled via GameObject deactivation | Document in startup sequence: template input GameObjects are deactivated before TinyRiftScope.Awake() |
| Hold-to-aim state not flushed on unexpected disconnect | Low | Medium — skill doesn't fire | Subscribe to `InputSystem.onDeviceChange`, flush on device removed |
| Touch EnhancedTouch conflicts with other touch handlers | Low | Low — no other touch handlers in custom code | Test on mobile target early |

## Performance Implications

| Metric | Before | Expected After | Budget |
|--------|--------|---------------|--------|
| CPU (per frame) | N/A | ~0.01ms (Vector2 read + optional event dispatch) | 0.05ms |
| Memory | N/A | ~5KB (InputActionAsset + action map objects + callback wiring) | 50KB |
| GC (per frame) | N/A | 0 — no allocations in polling path. Event dispatches allocate `Action<T>` delegate (one-time per subscription) | 0 |

## Migration Plan

1. Create `Assets/_TinyRift/Resources/Input/TinyRiftInput.inputactions` with three action maps per GDD spec
2. Create `InputRouter.cs` in `Assets/_TinyRift/Runtime/Foundation/Input/` implementing `IInputRouter`
3. Create `IInputRouter.cs` interface file
4. Add `InputRouter` component to the TinyRiftScope GameObject in the startup scene
5. Wire `GameStateChangedEvent` subscription in `Start()` (Event Bus exists per ADR-002)
6. Disable template `PCInputController`/`PCSkillController` GameObjects in `_TinyRift` scenes
7. Test KBM input in Editor
8. Test gamepad input with connected controller
9. Test touch input on mobile build

**Rollback plan**: Remove `InputRouter` from TinyRiftScope GameObject. Systems receive zero input — no crash, just no movement/actions. Add a debug key handler on a temporary GameObject to unblock development.

## Validation Criteria

- [ ] No `Input.GetKey`, `Input.GetMouseButton`, `Input.GetAxis`, or any `Input.*` calls in `Assets/_TinyRift/`
- [ ] GState transition from InRun → Menu disables Move and Aim within 1 frame (verified in test)
- [ ] GState transition from Menu → InRun enables Gameplay map before auto-attack resumes (event bus dispatch order verified)
- [ ] Move input during Menu is silently dropped
- [ ] Pressing Escape during InRun calls `IGameStateManager.TransitionTo(Paused)`
- [ ] Hold-to-aim skill fires correctly on release with last known aim direction
- [ ] Hold-to-aim state is flushed on map disable (e.g., pause while holding)
- [ ] Device disconnect during hold-to-aim releases the skill
- [ ] Touch input works on mobile build (EnhancedTouch)
- [ ] Rebinding overrides save/load correctly (post-MVP)

## GDD Requirements Addressed

| GDD Document | System | Requirement | How This ADR Satisfies It |
|-------------|--------|-------------|--------------------------|
| `design/gdd/input-system.md` | Input System | Single entry point wrapping Input System 1.19.0 | InputRouter wraps InputActionAsset, all physical input routed through it |
| `design/gdd/input-system.md` | Input System | GState-driven map switching via Event Bus | InputRouter subscribes to GameStateChangedEvent, calls SetActionMap() |
| `design/gdd/input-system.md` | Input System | Three action maps: Gameplay, Menu, Camp | Defined in custom .inputactions asset |
| `design/gdd/input-system.md` | Input System | Polling for Move/Aim, events for skill activation | IInputRouter exposes both polling methods and C# events |
| `design/gdd/input-system.md` | Input System | Device auto-detection | ctx.control.device checked on each callback |
| `design/gdd/input-system.md` | Input System | No modification to template input controllers | Template controllers disabled via GameObject deactivation |
| `design/gdd/game-state-manager.md` | Game State | Input Map switching on GState transitions | InputRouter subscribes to GameStateChangedEvent |
| `design/gdd/event-bus.md` | Event Bus | Interact/OpenCodex/StartRun published as struct events | InputRouter publishes action events via IEventBus |

## Related

- ADR-001: VContainer DI — InputRouter registered in TinyRiftScope Foundation layer
- ADR-002: Event Bus — InputRouter subscribes to GameStateChangedEvent, publishes action events
- `architecture.md:161` — Foundation layer includes Input
- `design/gdd/input-system.md` — Full GDD with action maps, IInputRouter interface, edge cases
- `docs/engine-reference/unity/modules/input.md` — Verified API reference for Input System 1.19.0
