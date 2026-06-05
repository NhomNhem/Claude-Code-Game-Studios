# Control Manifest

> **Engine**: Unity 6000.3.11f1 (URP 17.3, Input System 1.19.0)
> **Last Updated**: 2026-06-01
> **Manifest Version**: 2026-06-01
> **ADRs Covered**: ADR-001 (VContainer DI), ADR-002 (Event Bus), ADR-003 (Input System), ADR-004 (Time System), ADR-005 (Object Pooling), ADR-006 (Save/Profile)
> **Status**: Active — regenerate with `/create-control-manifest` when ADRs change

`Manifest Version` is the date this manifest was generated. Story files embed this date when created. `/story-readiness` compares a story's embedded version to this field to detect stories written against stale rules.

This manifest is a programmer's quick-reference extracted from all Accepted ADRs, technical preferences, and engine reference docs. For the reasoning behind each rule, see the referenced ADR.

---

## Foundation Layer Rules

*Applies to: DI registration, input routing, time management, object pooling, save/load, engine initialisation*

### Required Patterns

#### DI & Registration (ADR-001)
- Interfact-first: every public system must have an interface. Consumers never reference concrete types. Exception: Presentation-layer controllers that are Event Bus subscribers only. — source: ADR-001
- One registration per file. If a system needs conditional registration, extract into a private method. — source: ADR-001
- Foundation registration batch is order-independent. VContainer resolves dependencies at construction time. — source: ADR-001
- `PoolManager.ClearAll()` must be called explicitly on scene transitions by SceneManager. — source: ADR-001
- `IEventBus.Clear()` is explicit per scope. SceneManager calls it on transition. — source: ADR-001
- Add a static AOT-code-generation method in TinyRiftScope that forces IL2CPP to preserve `ObjectPool<T>` for each concrete T used at runtime. — source: ADR-001
- VContainer source generators are required for IL2CPP/AOT builds. Install `VContainer.SourceGenerator` NuGet package and enable in `VContainerSettings`. — source: ADR-001
- `BackendBootstrap` uses VContainer's `IAsyncStartable` (returns `UnityEngine.Awaitable` on Unity 6000.x). — source: ADR-001
- Scene-scoped components must resolve services from TinyRiftScope via explicit VContainer injection or Find on the DontDestroyOnLoad scope. — source: ADR-001
- Layer boundaries enforced by convention (code review), not by DI container. — source: ADR-001
- Never modify code in `Assets/BulletHellTemplate/`. — source: ADR-001

#### Input System (ADR-003)
- `Input.GetKey`, `Input.GetMouseButton`, `Input.GetAxis` must never appear in custom code. — source: ADR-003
- `InputActionAsset` as serialized reference: `[SerializeField] private InputActionAsset _inputAsset`. Asset lives in `Assets/_TinyRift/Resources/Input/`. — source: ADR-003
- On GState change: `DisableAll() → Enable(newMap) → ResetDevice()`. Three maps: Gameplay (InRun), Menu (Menu/Paused/Victory/Defeat), Camp (HeroCamp). — source: ADR-003
- Movement input = polling (per-frame Vector2). Skill activation = events (one-shot). — source: ADR-003
- Track device from callback context (`ctx.control.device`) for future button prompt display. No per-device branching in consumers. — source: ADR-003
- Hold-to-aim: on performed set flag, on canceled route skill with lastAimDir, on map disable flush all held skills. — source: ADR-003
- Enable `EnhancedTouchSupport` in `InputRouter.Awake()`. — source: ADR-003
- Rebinding deferred to post-MVP. Use `SaveBindingOverridesAsJson()` / `LoadBindingOverridesFromJson()` with PlayerPrefs. — source: ADR-003
- `builder.RegisterComponentInHierarchy<InputRouter>().As<IInputRouter>()`. InputRouter must exist in the startup scene. — source: ADR-003
- UI navigation via `InputSystemUIInputModule` (standard Unity pattern). — source: ADR-003
- Template PCInputController/PCSkillController GameObjects deactivated before TinyRiftScope.Awake(). — source: ADR-003
- Movement input only during InRun/HeroCamp. Skill input only during InRun. UI navigation only during Menu/Paused/Victory/Defeat. — source: ADR-003

#### Time System (ADR-004)
- `Time.timeScale` must never be written outside `TimeManager`. — source: ADR-004
- All time queries route through `ITimeManager`. — source: ADR-004
- Save pre-pause scale (including pre-hit-stop scale if hit-stop was active) on pause entry; restore on exit. — source: ADR-004
- `TriggerHitStop(float duration, float timeScale = 0f)` — last call wins. Pre-hit-stop scale preserved. — source: ADR-004
- Hit-stop duration tracked in unscaled time — hit-stop must expire even if the game is frozen visually. — source: ADR-004
- Cooldowns decrement by `Time.deltaTime` each frame. At `Time.deltaTime == 0` (pause), cooldowns do not tick. — source: ADR-004
- Run timer: scaled timer freezes on pause; unscaled timer runs through everything. Resets on InRun entry, stops on InRun exit (except pause). — source: ADR-004
- Detect external `Time.timeScale` modifications and warn via `Debug.LogWarning`. — source: ADR-004
- Cooldown ID naming: prefix with system name (e.g., `"orbit_slot_0"`, `"burst_skill_fireball"`). — source: ADR-004

#### Object Pooling (ADR-005)
- Wrap `UnityEngine.Pool.ObjectPool<T>`. Do not write a custom pool. Each prefab maps to one `ObjectPool<T>`. T is the MonoBehaviour on the prefab root. — source: ADR-005
- SceneManager calls `PoolManager.EnsureCapacity()` for each entry in the scene's PoolProfile after `ClearAll()` and before scene gameplay systems activate. — source: ADR-005
- Pooled objects implement `IPoolable` with `OnSpawned()` / `OnDespawned()` callbacks. — source: ADR-005
- Three return paths: Explicit (`PoolManager.Return`), Timer (OnSpawned starts coroutine), Safety net (OnDisable detection). — source: ADR-005
- In `Get<T>()`, check `obj != null && obj.gameObject != null` before returning. Prune null entries from pool's internal stack. — source: ADR-005
- PoolManager is event-bus agnostic. Pooled objects may publish events but PoolManager itself never touches the bus. — source: ADR-005
- AOT preservation list must be updated whenever a new pool type is added. CI should grep for `ObjectPool<` in `_TinyRift/` and cross-reference against `PoolAotHelper.PreserveTypes()`. — source: ADR-005
- Configurable batch size with warning when exhausted. Pre-warm counts per scene via PoolProfile ScriptableObject. — source: ADR-005
- Zero GC allocation per `Get()` / `Return()` on hot path. Allocations happen at pool creation and growth only. — source: ADR-005
- PoolManager handles `Assets/_TinyRift/` content only. Template's MonsterPool/DropPool are separate. — source: ADR-005
- `ClearAll()` explicit on scene transitions. NOT cleaned up by scope disposal. Called by SceneManager at scene transition boundary (not mid-frame). — source: ADR-005
- Prefab root component is the pool type (convention-based). — source: ADR-005

#### Save/Profile — Persistence (ADR-006)
- `IPersistStateService` registers in Foundation layer. — source: ADR-006
- JSON via Newtonsoft.Json (`com.unity.nuget.newtonsoft-json`) as the sole serialization engine. All save files are plain-text JSON. — source: ADR-006
- All persistent data lives in one file: `Application.persistentDataPath/persistent.json`. — source: ADR-006
- Separate ephemeral `runstate.json`. Deleted on Defeat/Victory after `persistent.json` is verified written. — source: ADR-006
- Atomic temp → rename write: serialize to `.tmp`, verify SHA256, `File.Delete(dest)`, `File.Move(tmp, dest)`. No reliance on `overwrite:true`. — source: ADR-006
- Versioned schema with `saveVersion`. Loaded version < current → sequential migrations. Loaded version > current → reject, initialize defaults. — source: ADR-006
- Migration via `JsonConvert.DeserializeObject<T>()` only. Never `JObject.ToObject<T>()` or `Populate()` — source: ADR-006
- Backup before migration: `File.Copy` → migrate in-memory → atomic write. On failure restore backup. — source: ADR-006
- Dirty-flag + debounce coalescing: default 100ms, settings writes 500ms. — source: ADR-006
- All serialized fields use `[JsonProperty]` annotations. — source: ADR-006
- `MissingMemberHandling.Ignore` for deserialization. — source: ADR-006
- All async methods accept `CancellationToken`. — source: ADR-006

### Forbidden Approaches
- **Never** extend `BackendLifetimeScope` (violates template immutability). — source: ADR-001
- **Never** use Singletons / Service Locator for cross-system resolution. — source: ADR-001
- **Never** use per-layer child scopes (over-engineered for solo/small-team). — source: ADR-001
- **Never** use `Input.GetKey`, `Input.GetMouseButton`, `Input.GetAxis`. — source: ADR-003
- **Never** use generated C# class from `.inputactions` asset. — source: ADR-003
- **Never** use Unity `PlayerInput` component. — source: ADR-003
- **Never** write `Time.timeScale =` outside `TimeManager.cs`. — source: ADR-004
- **Never** build a separate hit-stop manager separate from time-scale manager. — source: ADR-004
- **Never** use unscaled deltaTime for all systems (hit-stop is required for Pillar 3). — source: ADR-004
- **Never** write a custom object pool from scratch. — source: ADR-005
- **Never** reuse template's MonsterPool/DropPool for custom content. — source: ADR-005
- **Never** use per-scene pools via VContainer child scopes (already resolved as app-scoped). — source: ADR-005
- **Never** use `BinaryFormatter` (removed in .NET 5+, unsafe). — source: ADR-006
- **Never** use `JsonUtility` for serialization (use Newtonsoft.Json). — source: ADR-006
- **Never** split saves into multiple files (no cross-field atomicity). — source: ADR-006
- **Never** use `JObject.ToObject<T>()` or `Populate()` (uses `Reflection.Emit`, breaks under IL2CPP). — source: ADR-006

### Performance Guardrails
| System | Budget | Source |
|--------|--------|--------|
| DI startup (35+ registrations) | < 5ms | ADR-001 |
| DI scope + registration data | < 50KB | ADR-001 |
| Input processing (per frame) | < 0.05ms | ADR-003 |
| Time system (per frame) | < 0.01ms | ADR-004 |
| Cooldown tracking | < 100 entries, ~32 bytes each | ADR-004 |
| Object pool Get/Return (per call) | < 0.01ms | ADR-005 |
| Scene transition ClearAll (200 objects) | < 1ms | ADR-005 |
| Save serialization | sub-ms for < 1KB payload | ADR-006 |
| Save disk writes | max 10 writes/second (debounced) | ADR-006 |
| Network sync | min 15-min interval, < 2KB payload | ADR-006 |

---

## Core Layer Rules

*Applies to: event bus messaging, profile sync, cross-domain orchestration*

### Required Patterns

#### Event Bus (ADR-002)
- Subscribe in Awake/Start, never constructor. VContainer injection happens after construction; `Subscribe<T>()` before Awake() is a silent no-op. — source: ADR-002
- Store the IDisposable token from `Subscribe<T>()`. Dispose in OnDestroy() or at scope teardown. — source: ADR-002
- Use `Subscribe(object, Action<T>)` overload as default. Enables `UnsubscribeAll(owner)` and WeakReference dead-subscriber pruning. — source: ADR-002
- Never allocate closure lambdas. Use `_bus.Subscribe<DamageEvent>(Handle)` (method group). — source: ADR-002
- Define events near their publisher. Not in a central Events.cs file. — source: ADR-002
- No event batching. Each `Publish<T>()` dispatches immediately. No end-of-frame queue. — source: ADR-002
- VContainer dual-interface registration: EventBus registers as both `IEventBus` and `ISubscriber`. Consumer-only systems get `ISubscriber` injected — no `Publish()` access. — source: ADR-002
- All events use `readonly record struct` with `Event` suffix. Fields are positional constructor parameters. — source: ADR-002
- Zero heap allocation per `Publish<T>()` — structs passed by `in` (readonly reference). — source: ADR-002
- A single broken subscriber must never kill the bus — per-subscriber try/catch in dispatch loop. — source: ADR-002
- Reentrant publishes must be safe up to depth 16 — ThreadStatic depth counter. — source: ADR-002
- `Clear()` deferred during publish cycle. Waits for current cycle to complete then clears. — source: ADR-002
- AOT preservation via link.xml + static method: preserve all `Action<T>` delegate types and event structs. — source: ADR-002
- Event struct size: keep under 64 bytes. — source: ADR-002
- Ordered processing uses pipeline-pattern events: `BeforeX, X, AfterX`. — source: ADR-002

#### Profile Sync (ADR-006)
- `IProfileSyncService` registers in Core layer. — source: ADR-006
- Save/Profile knows nothing about transport (ProfileSyncService knows nothing about disk layout). — source: ADR-006
- Server-authoritative balance: client reports earnings deltas, never pushes absolute balance. Server tracks `totalEarnedPerDevice[deviceId]`. — source: ADR-006
- Minimum sync interval: 15 minutes per device. Rolling cap: 50,000 gold per 24 hours. — source: ADR-006
- Conflict resolution per field type: Scalar = newest-wins timestamp; Progression = union-merge (append-only); Cumulative = additive merge; Composite = per-field rules. — source: ADR-006
- Sync queue (`.synclog`): append-only, atomic write, replayed on app start, entries merged before sending, pruned after server confirmation, last-attempt expiry. — source: ADR-006
- `.synclog` max 100 entries before forced sync. Max 5MB file size before truncation. — source: ADR-006

### Forbidden Approaches
- **Never** use a single `IEventBus` interface (no split interface) — consumers could accidentally call `Publish<T>()`. — source: ADR-002
- **Never** centralize events in an `Events.cs` file. — source: ADR-002
- **Never** defer event dispatch (no end-of-frame queue). — source: ADR-002
- **Never** push absolute balance values from client (allows fraud). — source: ADR-006

### Performance Guardrails
| System | Budget | Source |
|--------|--------|--------|
| Event publish (5 handlers) | < 0.01ms per publish | ADR-002 |
| Event struct size | < 64 bytes | ADR-002 |
| Profiling threshold | 0.5ms/handler (surfaced, not blocking) | ADR-002 |
| Network sync payload | < 2KB per sync | ADR-006 |
| Network sync interval | min 15 min | ADR-006 |

---

## Feature Layer Rules

*Applies to: combat, skills, enemy AI — No ADRs yet written*

Feature-layer ADRs (Damage Pipeline, Orbit Combat, Burst Skill, Rune Draft, Enemy AI, Wave Spawning) are deferred until Foundation/Core coding is underway. No rules defined yet.

---

## Presentation Layer Rules

*Applies to: rendering, audio, UI, VFX, shaders — No ADRs yet written*

UI Toolkit runtime pattern and screen shake profiles deferred to implementation. No rules defined yet.

---

## Global Rules (All Layers)

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `PlayerController` |
| Public fields/properties | PascalCase | `MoveSpeed` |
| Private fields | `_camelCase` | `_moveSpeed` |
| Methods | PascalCase | `TakeDamage()` |
| Files | PascalCase matching class | `PlayerController.cs` |
| Prefabs/Scenes | PascalCase matching root MonoBehaviour | `PlayerController.prefab` |
| Constants | PascalCase or UPPER_SNAKE_CASE for bitflags | `MaxHealth`, `FLAG_INVULNERABLE` |

### Performance Budgets

| Target | Value |
|--------|-------|
| Framerate (PC) | 60 FPS |
| Framerate (mobile) | 30 FPS |
| Frame budget (PC) | 16.6ms |
| Frame budget (mobile) | 33.3ms |
| Draw calls (mobile) | < 300 |
| Draw calls (PC) | < 500 |
| Memory ceiling (mobile) | 512 MB |
| Memory ceiling (PC) | 2 GB |

### Approved Libraries / Addons

| Library | Purpose | Notes |
|---------|---------|-------|
| `VContainer` | DI container | Bundled in template. SourceGenerator required for IL2CPP. |
| `UniTask` | Async operations | Bundled in template. |
| `com.unity.nuget.newtonsoft-json` | JSON serialization | Bundled in template. Pin to bundled version. |
| `com.unity.inputsystem` | Input handling | Version 1.19.0. Full KBM, Gamepad, Touch support. |
| `UnityEngine.Pool.ObjectPool<T>` | Object pooling | Built-in Unity API. |

### Forbidden APIs (Unity 6000.3.11f1)

These APIs are deprecated or unverified for Unity 6000.3.11f1:

| API | Replacement | Reason |
|-----|-------------|--------|
| `Input.GetKey()` | `Keyboard.current[Key.X].isPressed` | Deprecated |
| `Input.GetKeyDown()` | `Keyboard.current[Key.X].wasPressedThisFrame` | Deprecated |
| `Input.GetMouseButton()` | `Mouse.current.leftButton.isPressed` | Deprecated |
| `Input.GetAxis()` | `InputAction` callbacks | Deprecated |
| `Input.mousePosition` | `Mouse.current.position.ReadValue()` | Deprecated |
| `Canvas` (UGUI) | `UIDocument` (UI Toolkit) | Deprecated — UI Toolkit production-ready |
| `Text` component | `TextMeshPro` or UI Toolkit `Label` | Deprecated |
| `Image` component | `VisualElement` with background | Deprecated |
| `Resources.Load()` | `Addressables.LoadAssetAsync()` | Deprecated |
| `WWW` class | `UnityWebRequest` | Deprecated |
| `Application.LoadLevel()` | `SceneManager.LoadScene()` | Deprecated |
| `Legacy Animation` | `Animator Controller` | Deprecated |
| `Legacy Particle System` | `Visual Effect Graph` | Deprecated |
| `CommandBuffer.DrawMesh()` | RenderGraph API | Deprecated in URP 17 |
| `OnPreRender()` / `OnPostRender()` | `RenderPipelineManager` callbacks | Deprecated |
| `Physics.RaycastAll()` | `Physics.RaycastNonAlloc()` | GC allocation |
| `JObject.ToObject<T>()` | `JsonConvert.DeserializeObject<T>()` | Breaks IL2CPP (uses Reflection.Emit) |
| `Populate()` | Manual field mapping | Breaks IL2CPP (uses Reflection.Emit) |
| `BinaryFormatter` | JSON + Newtonsoft.Json | Removed in .NET 5+, unsafe |

### Cross-Cutting Constraints

- **No closure lambdas in Event Bus Subscribe calls** — use method groups only. — source: ADR-002
- **Grep for `Time.timeScale =` in `Assets/_TinyRift/`** — only `TimeManager.cs` may contain it. — source: ADR-004
- **CI must validate**: IL2CPP server build compiles cleanly, `link.xml` preserves all event types, AOT preservation list covers all `ObjectPool<T>` concrete types. — source: ADR-001, ADR-002, ADR-005
- **Shutdown hooks** (`Application.wantsToQuit`) block until pending save write completes. — source: ADR-006
- **File.Move with `overwrite:true` not reliably atomic** on iOS/Android — use explicit temp→delete→move pattern. — source: ADR-006
- **No runtime code generation** (AOT safety). VContainer.SourceGenerator must be used for IL2CPP builds. — source: ADR-001
- **IL2CPP build must compile cleanly before any release merge**. — source: ADR-001
