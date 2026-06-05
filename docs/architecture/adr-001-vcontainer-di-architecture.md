# ADR-001: VContainer DI Architecture & Service Registration

## Status

Accepted

## Date

2026-06-01

## Decision Makers

user + agents (technical-director, unity-specialist, architecture-decision skill)

## Summary

Resolve the two-scope VContainer conflict between the template's `BackendLifetimeScope` (owner of `IBackendService`) and the 35+ custom systems requiring DI. Establishes a parent-child scope hierarchy: `BackendLifetimeScope → TinyRiftScope`, with all custom systems registered as interface singletons in the child scope, and explicit scope lifecycle rules for cross-scene services.

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Core (DI Framework) |
| **Knowledge Risk** | LOW — VContainer is third-party, bundled in template at `Assets/BulletHellTemplate/ThirdPartyResources/Tools/VContainer/` |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md`, template code: `BackendLifetimeScope.cs`, `BackendBootstrap.cs` |
| **Post-Cutoff APIs Used** | None — VContainer APIs are library-defined, not engine-version-dependent |
| **Verification Required** | IL2CPP builds must include VContainer.SourceGenerator (see Risks) |

> **Note**: VContainer source generators are required for IL2CPP/AOT builds. The bundled VContainer supports `System.Reflection.Emit` fallback, which does not work under IL2CPP. Install `VContainer.SourceGenerator` NuGet package and enable in `VContainerSettings` ScriptableObject. Add to CI validation: an IL2CPP server build must compile cleanly before any release merge.

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | None (first Foundation ADR) |
| **Enables** | ADR-002 (Event Bus), ADR-003 (Input System), ADR-004 (Time System), ADR-005 (Object Pooling), ADR-006 (Save/Profile) |
| **Blocks** | All Foundation layer stories, all Feature/Presentation registration work |
| **Ordering Note** | Must be Accepted before any Foundation-layer system is implemented — code cannot be written without knowing which scope and registration pattern to use |

## Context

### Problem Statement

The template ships with `BackendLifetimeScope` (a VContainer `LifetimeScope` in `Assets/BulletHellTemplate/Core/DataHandler/`) that registers only `BackendSettings`, `IBackendService` (implementation selected by `BackendOption`), and `BackendManager`. Our custom code needs a DI scope for all 35+ MVP systems across four layers (Foundation/Core/Feature/Presentation). The template boundary rule ("never modify template code") means we cannot add registrations to `BackendLifetimeScope`. Without a clear scope architecture, developers will either:
- Add registrations to the wrong scope (mixing template and custom)
- Use singletons and Service Locator patterns (reducing testability)
- Create conflicting scope hierarchies (multiple independent LifetimeScopes)

### Current State

- `BackendLifetimeScope` exists in template code, registers 3 types
- `BackendBootstrap.cs` exists as a plain C# class with constructor injection (`BackendSettings`, `IBackendService`), called externally
- No unified scope for custom systems — 20+ GDDs reference VContainer registration but have no concrete scope to register into
- No `TinyRiftScope` exists yet
- No `Assets/_TinyRift/Runtime/Bootstrap/` directory exists for scope/wiring code

### Constraints

- **Template boundary**: Never modify `Assets/BulletHellTemplate/` code. The template's `BackendLifetimeScope` is immutable.
- **Cross-scene services**: Event Bus, Network Manager, Currency Service, Account Service must survive scene loads (game data, connection state)
- **Scene-scoped services**: PoolManager needs scene-specific pools (different enemies, VFX per scene) — but cleanup is explicit via `ClearAll()`, not scope disposal
- **AOT safety**: IL2CPP builds cannot use runtime code generation. VContainer's `ReflectionInjector` fallback (uses `System.Reflection.Emit`) will fail under IL2CPP.
- **Performance**: DI resolution must not add measurable startup time. 35+ singleton registrations is negligible (metadata-only until first resolve).

### Requirements

- All custom systems must have a home scope that respects the template boundary
- Systems must register as interfaces — consumers depend on abstractions, not concrete types
- Foundation-layer registration must be order-independent within the layer
- Scope must support `IAsyncStartable` entry points for async startup (backend init, asset loading)
- Must work correctly with IL2CPP/AOT builds
- Must resolve open question QQ-03 from architecture.md: Event Bus `Clear()` behavior
- Must not back the Lead Programmer's Service Locator anti-pattern concern

## Decision

Use a **two-scope VContainer hierarchy** with `BackendLifetimeScope` as parent and `TinyRiftScope` as child (DontDestroyOnLoad, app lifetime). All custom systems register as interface-to-implementation singletons in `TinyRiftScope`, grouped by layer in separate configuration methods.

### Architecture

```
BackendLifetimeScope (parent - template, scene-placed)
  ├── BackendSettings (ScriptableObject instance)
  ├── IBackendService → WebSocketSqlBackendService | OfflineBackendService | FirebaseBackendService
  │     (selected by BackendSettings.option)
  └── BackendManager (ComponentInHierarchy)
       │
       └── [parent reference] ─────────────────────────────┐
                                                            ▼
                              TinyRiftScope (child - custom, DontDestroyOnLoad)
                              ├── Foundation (order-independent batch)
                              │   IEventBus         → EventBus
                              │   IGameStateManager → GameStateManager
                              │   ITimeManager      → TimeManager
                              │   IInputRouter      → InputRouter (wraps Input System)
                              │   IHitDetectionService → HitDetectionService
                               │   IPoolManager      → PoolManager
                               │   ISkillRegistry    → SkillRegistry
                               │   INetworkManager   → NetworkManager (note: deviates from
                               │                         architecture.md AppScope — functionally
                               │                         equivalent, see deviation note below)
                               │   IPersistStateService → SaveManager
                               ├── Core (dependency order)
                               │
                              │   IAccountService   → AccountService
                              │   IZoneDefinitionRegistry → ZoneRegistry (IInitializable)
                              │   IWorldStateService → WorldStateService
                              │   IAudioService     → AudioService
                              │   IVfxService       → VfxService
                              │   ICurrencyService  → CurrencyService
                              │   ILoreService      → LoreService
                              │   IStatusFXService  → StatusFXService
                              │   IBuildStateService → BuildStateService
                              ├── Feature
                              │   IDamageHealthService   → DamageHealthService
                              │   IOrbitCombatService    → OrbitCombatService
                              │   IBurstSkillService     → BurstSkillService
                              │   ILevelUpService        → LevelUpService
                              │   IRuneDraftService      → RuneDraftService
                              │   IEnemyAIService        → EnemyAIService
                              │   IWaveSpawningService   → WaveSpawningService
                              │   IBossEncounterService  → BossEncounterService
                              │   IScreenShakeService    → ScreenShakeService
                              │   ICampService           → CampService
                              │   IZoneRestorationService → ZoneRestorationService
                              └── Presentation (Event Bus subscribers + interface queries)
                                  HUDController
                                  DraftUIController
                                  CampMenuController
                                  CodexController
                                  Adapter (SkillPresentationAdapter)
                                  LoadingScreenController
                                  RunCompleteController
                                  SceneManager
```

**Deviation note — INetworkManager scope**: The architecture doc (`architecture.md:159`) and Network Manager GDD (`network-manager.md:26`) specify registration at "app-scope" (BackendLifetimeScope). This ADR places `INetworkManager` in TinyRiftScope instead. The effect is identical because TinyRiftScope persists across all scene loads (DontDestroyOnLoad). The benefit: `INetworkManager` resolves alongside all other custom systems, enabling cleaner test setup without cross-scope resolution. The GDD has been updated to reflect this (see GDD Sync section).

### Key Interfaces

```csharp
public sealed class TinyRiftScope : LifetimeScope
{
    protected override void Configure(IContainerBuilder builder)
    {
        ConfigureFoundation(builder);
        ConfigureCore(builder);
        ConfigureFeature(builder);
        ConfigurePresentation(builder);

        builder.RegisterEntryPoint<BackendBootstrap>();
    }

    private void ConfigureFoundation(IContainerBuilder builder)
    {
        builder.Register<EventBus>(Lifetime.Singleton).As<IEventBus>();
        builder.Register<GameStateManager>(Lifetime.Singleton).As<IGameStateManager>();
        builder.Register<TimeManager>(Lifetime.Singleton).As<ITimeManager>();
        builder.Register<InputRouter>(Lifetime.Singleton).As<IInputRouter>();
        builder.Register<HitDetectionService>(Lifetime.Singleton).As<IHitDetectionService>();
        builder.Register<PoolManager>(Lifetime.Singleton).As<IPoolManager>();
        builder.Register<SkillRegistry>(Lifetime.Singleton).As<ISkillRegistry>();
        builder.Register<NetworkManager>(Lifetime.Singleton).As<INetworkManager>();
        builder.Register<SaveManager>(Lifetime.Singleton).As<IPersistStateService>();
    }

    private void ConfigureCore(IContainerBuilder builder)
    {
        builder.Register<AccountService>(Lifetime.Singleton).As<IAccountService>();
        // ...
    }

    private void ConfigureFeature(IContainerBuilder builder)
    {
        builder.Register<DamageHealthService>(Lifetime.Singleton).As<IDamageHealthService>();
        builder.Register<OrbitCombatService>(Lifetime.Singleton).As<IOrbitCombatService>();
        // ...
    }

    private void ConfigurePresentation(IContainerBuilder builder)
    {
        builder.Register<HUDController>(Lifetime.Singleton);
        builder.Register<DraftUIController>(Lifetime.Singleton);
        builder.Register<SceneManager>(Lifetime.Singleton);
        // ...
    }
}
```

### BackendBootstrap (IAsyncStartable)

```csharp
public sealed class BackendBootstrap : IAsyncStartable
{
    private readonly IBackendService _backend;
    private readonly BackendSettings _settings;

    public BackendBootstrap(IBackendService backend, BackendSettings settings)
    {
        _backend = backend;
        _settings = settings;
    }

    public async Awaitable StartAsync()
    {
        await InitializeAsync();
    }

    private async UniTask<bool> InitializeAsync()
    {
        // Login flow, account data load, presence update
        // See BackendBootstrap.cs for full implementation
    }
}
```

Registered via `builder.RegisterEntryPoint<BackendBootstrap>()` — VContainer's `IAsyncStartable` returns `UnityEngine.Awaitable` on Unity 6000.x (via `UNITY_2023_1_OR_NEWER` preprocessor). This runs after scope build without blocking scene loading.

### Implementation Guidelines

1. **Interface-first**: Every public system must have an interface. Consumers never reference concrete types. Exception: Presentation-layer controllers that are Event Bus subscribers only (they depend on IEventBus, not the concrete system).
2. **One registration per file**: Each system's registration is a single line. If a system needs conditional registration (e.g., platform-dependent implementation), extract into a private method.
3. **Foundation order**: The `ConfigureFoundation` batch is order-independent. VContainer resolves dependencies at construction time, not registration time. Registration order within the method does not matter.
4. **PoolManager ClearAll()**: Unlike scope-disposal cleanup (which does not happen for app-scoped TinyRiftScope), `PoolManager.ClearAll()` must be called explicitly on scene transitions by `SceneManager`. This replaces the GDD's original "cleanup via scope dispose" mechanism.
5. **Event Bus Clear()**: QQ-03 resolved — `Clear()` is explicit per scope. SceneManager calls `IEventBus.Clear()` on transition, not `SceneManager.sceneLoaded` hook.
6. **AOT code stripping**: Add a static AOT-code-generation method in TinyRiftScope (or a dedicated AOT helper) that forces IL2CPP to preserve `ObjectPool<T>` for each concrete `T` used at runtime. See `design/gdd/object-pooling.md` Rule 11.

## Alternatives Considered

### Alternative 1: Single scope — extend BackendLifetimeScope

- **Description**: Add a `partial class BackendLifetimeScope` in `Assets/_TinyRift/` that extends the template scope's configuration.
- **Pros**: Single scope, simpler mental model.
- **Cons**: Requires `partial class` or editing template code. `BackendLifetimeScope` is not declared `partial` — would need to modify template. Even if possible, creates tight coupling between template and custom registration logic.
- **Estimated Effort**: Lower initially, higher maintenance cost.
- **Rejection Reason**: Violates the "never modify template" rule. Creates coupling that makes template upgrades harder.

### Alternative 2: No DI — Singletons / Service Locator

- **Description**: Use `GameObject.FindObjectOfType`, `Singleton<T>`, or a custom `ServiceLocator` static class for service resolution.
- **Pros**: No DI framework knowledge required, simpler for junior developers.
- **Cons**: No testability (hard to mock singletons), no lifecycle management, no scope hierarchy. Template already uses VContainer — two competing service resolution patterns would confuse developers.
- **Estimated Effort**: Lower initially, much higher debugging cost.
- **Rejection Reason**: Template investment in VContainer would be wasted. Singleton pattern prevents parallel work and creates hidden coupling.

### Alternative 3: Per-layer child scopes

- **Description**: Instead of one TinyRiftScope with layer-grouped registration methods, create child scopes per layer: `FoundationScope → CoreScope → FeatureScope → PresentationScope`, each as a VContainer child of the previous.
- **Pros**: Container-level enforcement of layer dependency rules — a Presentation service cannot resolve a Feature service because child scopes only resolve upward.
- **Cons**: Significantly more scope objects, scene hierarchy clutter, harder to debug. Layer boundary violations can be caught in code review at lower complexity cost.
- **Estimated Effort**: Higher setup, lower ongoing enforcement cost.
- **Rejection Reason**: Over-engineered for a solo/small-team project. Layer enforcement via code review is sufficient and avoids unnecessary scope hierarchy complexity.

## Consequences

### Positive

- Clear separation between template-owned and custom-owned services
- Interface-first design enables unit testing via mock injection
- Foundation-layer registration order independence reduces coupling
- BackendLifetimeScope can be replaced or upgraded without affecting TinyRiftScope registrations
- Single child scope (not per-layer scopes) keeps the scope hierarchy flat and debuggable
- IAsyncStartable runs async startup without blocking scene load
- QQ-03 (Event Bus Clear) and LP Service Locator concern both resolved

### Negative

- Two scopes add mental overhead: developers must know which scope a service lives in
- Scene-scoped components (e.g., enemy MonoBehaviours in a scene prefab) must resolve services from TinyRiftScope, not the scene's auto-scope — requires explicit VContainer injection or Find on the DontDestroyOnLoad scope
- IAsyncStartable couples backend initialization timing to scope build (acceptable — startup is non-blocking)
- Layer boundaries are enforced by convention (code review), not by the DI container — a Presentation-layer class can inject a Feature-layer service directly. This is a conscious tradeoff to avoid per-layer scope complexity.

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| IL2CPP build fails without VContainer source generators | Medium | High — blocks release builds | Install VContainer.SourceGenerator, enable in VContainerSettings, add IL2CPP build to CI |
| PoolManager doesn't auto-clean on scene transition (scope never disposes) | Low | Medium — stale pooled objects accumulate | SceneManager calls PoolManager.ClearAll() explicitly. Unit test verifies. |
| New developer registers in wrong scope | Medium | Low — wrong scope usually still works (child resolves from parent) | Document scope responsibility in TinyRiftScope comments |
| TinyRiftScope GameObject destroyed accidentally (e.g., scene cleanup) | Low | High — all services lost | Use DontDestroyOnLoad + hideFlags. Add safety check in debug build. |

## Performance Implications

| Metric | Before | Expected After | Budget |
|--------|--------|---------------|--------|
| CPU (startup) | N/A | ~1ms for 35+ metadata-only registrations | 5ms (non-blocking) |
| Memory | N/A | ~2KB for scope + registration data | 50KB |
| Load Time | N/A | 0 — VContainer registers lazily (no instantiation until first resolve) | N/A |

## Migration Plan

1. Create `Assets/_TinyRift/Runtime/Bootstrap/TinyRiftScope.cs` with the registration methods shown above
2. Create `Assets/_TinyRift/Runtime/Bootstrap/TinyRiftScope.prefab` with DontDestroyOnLoad, parented to BackendLifetimeScope
3. Update `BackendBootstrap.cs` to implement `IAsyncStartable` (add method, keep existing async methods as private)
4. Update `PoolManager` to remove scene-scope assumptions — add documentation that `ClearAll()` is explicit
5. Update `SceneManager` (or equivalent scene transition code) to call `IEventBus.Clear()` and `IPoolManager.ClearAll()`
6. Install `VContainer.SourceGenerator` and enable in `VContainerSettings`
7. Add IL2CPP server build to CI pipeline

**Rollback plan**: Comment out the `TinyRiftScope` GameObject and fall back to per-system registration in `BackendLifetimeScope` via a wrapper partial class. This loses interface-first benefits but restores functionality.

## Validation Criteria

- [ ] `TinyRiftScope` resolves all 35+ registered services without throwing at startup
- [ ] Services injected via `IAsyncStartable` complete initialization without blocking scene rendering
- [ ] IL2CPP server build compiles cleanly with no AOT-related `ObjectPool<T>` or `Action<T>` stripping errors
- [ ] `PoolManager.ClearAll()` is called on scene transition and releases all pooled objects
- [ ] `IEventBus.Clear()` is called on scene transition and removes all subscribers
- [ ] BackendLifetimeScope services (`IBackendService`) are resolvable from TinyRiftScope (parent resolution works)
- [ ] No `MonoBehaviour` in the project uses `FindObjectOfType` or `Singleton<T>` for cross-system service resolution

## GDD Requirements Addressed

| GDD Document | System | Requirement | How This ADR Satisfies It |
|-------------|--------|-------------|--------------------------|
| `design/gdd/event-bus.md` | Event Bus | "registered as a VContainer singleton in TinyRiftScope" | TinyRiftScope registers `IEventBus → EventBus` as singleton |
| `design/gdd/game-state-manager.md` | Game State | "registered via VContainer in TinyRiftScope" | TinyRiftScope registers `IGameStateManager → GameStateManager` |
| `design/gdd/input-system.md` | Input System | "TinyRiftScope → Input — Registers IInputRouter as singleton" | TinyRiftScope registers `IInputRouter → InputRouter` |
| `design/gdd/object-pooling.md` | Object Pooling | Registration in TinyRiftScope + scene-scoped pool lifecycle | TinyRiftScope registers `IPoolManager → PoolManager`. Explicit `ClearAll()` replaces scope-disposal cleanup. GDD updated to match. |
| `design/gdd/network-manager.md` | Network Manager | "Registered at app-scope in VContainer" | Functionally identical: TinyRiftScope is cross-scene. GDD updated. |
| `design/gdd/time-system.md` | Time System | "Registration in TinyRiftScope" | TinyRiftScope registers `ITimeManager → TimeManager` |
| `design/gdd/hit-detection.md` | Hit Detection | "Scope → HitDetect Registration" | TinyRiftScope registers `IHitDetectionService → HitDetectionService` |
| `design/gdd/skill-data-system.md` | Skill Data | VContainer singleton for SkillRegistry | TinyRiftScope registers `ISkillRegistry → SkillRegistry` |
| 12+ Feature/Presentation GDDs | Various | Each specifies VContainer registration in a named scope | All reference "TinyRiftScope" which this ADR establishes |

> Foundational decision — no single GDD requirement drove this. It constrains and enables all 35 GDD systems. See individual GDD rows above for specific traceability.

## Related

- `architecture.md:159-168` — Initialization order diagram (this ADR implements)
- `architecture.md:235` — Required ADR #1
- `architecture.md:282` — QQ-03 resolved by this ADR
- `BackendLifetimeScope.cs` — Template scope this ADR parents to
- `BackendBootstrap.cs` — Converted to IAsyncStartable by this ADR
- `design/gdd/object-pooling.md` — Updated: PoolManager is cross-scene, not scene-scoped
- `design/gdd/network-manager.md` — Updated: registered in TinyRiftScope, not AppScope
- `docs/architecture/adr-006-save-profile-serialization.md` — Renames `IProfileService` → `IPersistStateService`, moves from Core → Foundation. This ADR updated to match. `IProfileSyncService` registers in Core per ADR-006.
