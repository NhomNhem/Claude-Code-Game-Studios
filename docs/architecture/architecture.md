# Tiny Rift Survivors — Master Architecture

## Document Status
- Version: 1.0
- Last Updated: 2026-05-30
- Engine: Unity 6000.3.11f1 (Unity 6 Update 3) — URP 17.3 — Input System 1.19.0
- GDDs Covered: 35 MVP systems (all GDDs in design/gdd/)
- ADRs Referenced: 6 Accepted (ADR-001 through ADR-006)
- Technical Director Sign-Off: 2026-06-02 — APPROVED (all 6 Foundation ADRs written and Accepted, open questions resolved)
- Lead Programmer Feasibility: FEASIBLE — 14 concerns raised, all resolvable with clear ADRs + ~3-5 days prep

## Engine Knowledge Gap Summary

**Unity 6000.3.11f1 is post-cutoff (LLM training ~2022 LTS).** Key HIGH RISK domains:

| Domain | Risk | Key Changes | Impacted Systems |
|--------|------|-------------|------------------|
| Input System 1.19.0 | HIGH | Legacy Input deprecated; `Keyboard.current`, `InputAction` callbacks | Input System, Burst Skill (aim), Draft Panel |
| URP 17.3 / RenderGraph | HIGH | RenderGraph replaces CommandBuffer for custom passes | VFX System, Screen Shake, Zone restore VFX |
| UI Toolkit 2.0 | HIGH | Production-ready runtime UI (replaces UGUI); UXML/USS workflow | HUD, Draft Panel, Camp Menu, Codex, Loading |
| IL2CPP / AOT | HIGH | Source-generated serialization; `link.xml` required; `ObjectPool<T>` stripping | Object Pooling, Event Bus, Save/Profile |
| Addressables | MEDIUM | Asset loading throws on failure by default; `TryLoad` variants | Asset loading pipeline |
| Physics (PhysX 5.1) | MEDIUM | Solver iterations 6→8 (trigger-based, unaffected) | Hit Detection |

> **⚠️ All HIGH RISK domains should be cross-referenced with `docs/engine-reference/unity/` before implementation.**

## System Layer Map

```
┌──────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                          │
│  HUD, Draft Panel UI, Camp Menu UI, Codex UI,                │
│  SkillPresentationAdapter, Loading/Transition,                │
│  Run Completion                                              │
├──────────────────────────────────────────────────────────────┤
│  FEATURE LAYER                                               │
│  Damage & Health, Orbit Combat, Burst Skill,                 │
│  Level-Up, Rune Draft, Enemy AI, Wave Spawning,              │
│  Boss Encounter, Screen Shake, Hero Camp Progression,        │
│  Build State                                                 │
├──────────────────────────────────────────────────────────────┤
│  CORE LAYER                                                  │
│  Scene Manager, Save/Profile, Account/Profile,               │
│  Zone Definition, World State, Audio System, VFX System,     │
│  Currency System, Lore Fragment, Status Effect               │
├──────────────────────────────────────────────────────────────┤
│  FOUNDATION LAYER                                            │
│  Input System, Game State Manager, Time System,              │
│  Network Manager, Event Bus, Skill Data System,              │
│  Hit Detection, Object Pooling                               │
├──────────────────────────────────────────────────────────────┤
│  PLATFORM LAYER                                              │
│  Unity Engine (6000.3.11f1, URP 17.3, Input System 1.19.0)   │
│  VContainer, UniTask, Unity Built-in APIs                    │
└──────────────────────────────────────────────────────────────┘
```

**Layer dependency rule:** Each layer depends only on layers below it. Presentation → Feature → Core → Foundation → Platform. No circular dependencies exist (verified in systems-index.md).

## Module Ownership

### Foundation Layer

| Module | Owns | Exposes | Engine APIs | Risk |
|--------|------|---------|-------------|------|
| **Input System** | `InputActionAsset`, action map lifecycle, held-aim state | `IInputRouter` (Move, Aim, Skill press/hold, events) | `InputAction`, `InputSystem.ResetDevice()`, `InputAction.performed` | ⚠️ HIGH |
| **Game State Manager** | `GameState` enum, `bossActive` flag, `pauseOrigin` | `IGameStateManager` (TransitionTo, CurrentState, events) | None (pure C#) | — |
| **Time System** | `Time.timeScale`, cooldown registry, run timer, hit-stop state | `ITimeManager` (cooldowns, elapsed time, hit-stop) | `Time.timeScale`, `Time.deltaTime`, `Time.unscaledDeltaTime` | — |
| **Network Manager** | `ConnectionState`, reconnect backoff timer, heartbeat | `INetworkManager` (Connect/Disconnect, State) | Wraps template `IBackendService` | — |
| **Event Bus** | Subscriber registry, reentrancy depth tracker | `IEventBus` (Publish, Subscribe, UnsubscribeAll, Clear) | None (pure C# + `WeakReference<T>`) | ⚠️ HIGH (AOT) |
| **Skill Data System** | `SkillDefinition` assets, `SkillDatabase`, `SkillRegistry` | `ISkillRegistry` (GetDefinition, CreateInstance, UpgradeInstance) | `ScriptableObject` | — |
| **Hit Detection** | Hitbox registration, per-target hit cooldown | `HitDetectionRegistry` (Register/Unregister/Clear), `HitEvent` | `Collider`, `OnTriggerEnter` | — |
| **Object Pooling** | Pool dictionaries, `PoolProfile` config, AOT type preservation | `PoolManager` (Get, Return, EnsureCapacity, ClearAll) | `UnityEngine.Pool.ObjectPool<T>` | ⚠️ HIGH (AOT) |

### Core Layer

| Module | Owns | Exposes | Consumes |
|--------|------|---------|----------|
| **Save/Profile** | JSON file I/O, dirty-flag debounce, schema version, merge strategies | `IProfileService` (LoadAsync/SaveAsync, Get/Set by type) | `IBackendService`, `INetworkManager.IsConnected` |
| **Account/Profile** | Auth tokens (SecurePrefs encrypted), login state, init-data coordinator | `IAccountService` (Login, Register, AutoLogin, Logout) | `INetworkManager.IsConnected`, `WebsocketAuthHandler` |
| **Scene Manager** | Scene load/unload, additive scene support, pending queue | `ISceneManager` (LoadZone, UnloadZone, ActivateScene) | `IGameStateManager`, `SceneRegistrySO` |
| **Zone Definition** | `ZoneDefinitionSO` assets, `IZoneDefinitionRegistry` | `IWaveTableProvider`, `IZoneAudioProvider`, `IZoneEnvironmentProvider` | Nothing (data provider) |
| **World State** | Zone completion state, unlock sequence | Publishes `ZoneRestoredEvent` | `IProfileService` (load/save) |
| **Audio System** | `AudioCueLibrary`, `MusicController` (2x AudioSource), mixer snapshots | PlayOneShot, CrossfadeTo, PlayElementAmbience | Event Bus (7 types), `IZoneAudioProvider` |
| **VFX System** | VFX prefab dictionary, elemental VFX library, ground decals | Consumes Event Bus events (6 types), resolves via `VfxProfileKey` | `PoolManager`, Event Bus |
| **Currency System** | Two currencies (Gold, Aether Shards), delta-reporting | Earn, Spend, CanAfford, GetBalance | `EntityDiedEvent`, `INetworkManager.IsConnected` |
| **Lore Fragment** | MemoryFragmentData assets, collection state, read state | `ILoreFragmentService` (GetCollected, GetByZone, MarkRead) | `EntityDiedEvent` (auto-collect) |
| **Status Effect** | Per-entity status tracker, element→status mapping, tick timers | `IStatusEffectService` (ApplyStatus, GetActiveStatuses, ClearAll) | `ElementType`, `ITimeManager` |

### Feature Layer

| Module | Owns | Exposes | Consumes |
|--------|------|---------|----------|
| **Damage & Health** | `HealthComponent` per entity, damage pipeline, i-frames | `HitEvent` → `DamageDealtEvent`, `EntityDiedEvent` | `ISkillRegistry`, `IStatusEffectService`, `PoolManager` |
| **Orbit Combat** | `OrbitRing` per orbit skill, projectile ring rotation, targeting | Manages `SkillType.Orbit` SkillInstances | `ISkillRegistry`, `HitDetectionRegistry`, `PoolManager`, `ITimeManager` |
| **Burst Skill** | Cooldown per burst skill, aim resolution, projectile spawn | TryActivate(skillId, AimData) | `ISkillRegistry`, `PoolManager`, `ITimeManager`, `IInputRouter` |
| **Level-Up** | XP accumulation, threshold curve, draft trigger | Consumes `EntityDiedEvent`, publishes `LevelUpEvent` | Event Bus |
| **Rune Draft** | Draft pool filter, rarity weighting (60/30/10), reroll state | `IDraftService` (GenerateDraft, CommitPick, Reroll) | `ISkillRegistry`, `IBuildStateService` |
| **Enemy AI** | Enemy state machines per type, elemental affinity | Behavior-driven by `EnemyDefinition` SO | `GameState.currentState`, `HitDetectionRegistry`, `PoolManager` |
| **Wave Spawning** | Wave lifecycle, spawn patterns, escalation | Spawns enemies per `IWaveTableProvider` | `IZoneDefinitionRegistry`, `PoolManager`, Event Bus |
| **Boss Encounter** | Boss lifecycle (phase tree), arena gating, telegraphs | Phase transitions, publishes `Victory` | `EnemyAI`, `IStatusEffectService` |
| **Screen Shake** | Shake profiles, hit-stop orchestration | Consumes `DamageDealtEvent`, `EntityDiedEvent` | `ITimeManager.TriggerHitStop()` |
| **Hero Camp Progression** | `UpgradeDefinition` assets, purchase state, stat bonuses | Purchase, GetLevel, GetStatBonus | `ICurrencyService`, `IProfileService` |
| **Build State** | Per-run `List<SkillInstance>`, burst slot map, upgrade tiers | AddSkill, UpgradeSkill, HasSkill, Clear | `ISkillRegistry` |

### Presentation Layer

| Module | Owns | Exposes | Consumes |
|--------|------|---------|----------|
| **HUD** | Canvas layout, HP/XP bars, currency, skill slots, damage numbers | N/A (read-only) | `GameState`, `BuildState`, `CurrencySystem`, `ITimeManager` |
| **Draft Panel UI** | 3-card layout, rarity glow, pick animation | N/A (read-only) | `IDraftService`, `ISkillRegistry` |
| **Camp Menu UI** | Tabbed interface (Upgrades/Codex/Map), start run button | N/A | `ICampProgressionService`, `ILoreFragmentService`, `ICurrencyService` |
| **Codex UI** | Zone-tabbed fragment grid, unread badges, rune↔text toggle | N/A | `ILoreFragmentService` |
| **SkillPresentationAdapter** | `PresentationProfile` data, `ProjectileRegistry` | Routes cast/hit VFX, audio, hit-stop | `HitEvent`, `SkillDefinition` keys, `PoolManager`, `ITimeManager` |
| **Loading/Transition** | Visual transition effects, scene activation gate | Transition callbacks | `ISceneManager`, `GameState` |
| **Run Completion** | Victory/Defeat summary screen, reward calc | N/A | `ICurrencyService`, `ILoreFragmentService`, `IWorldStateService` |

## Data Flow

### Frame Update Path

```
Input (Update) → CharacterEntity.Move/UseSkill
Orbit (LateUpdate) → rotate projectiles
Hit Detection (OnTriggerEnter) → HitEvent → Event Bus
  ├→ Damage & Health → DamageDealtEvent / EntityDiedEvent
  ├→ Status Effect → ApplyStatus
  ├→ Screen Shake → TriggerHitStop
  ├→ VFX System → PoolManager.Get<VfxController>
  ├→ Audio System → PlayOneShot
  ├→ Level-Up → XP accumulate → threshold → Draft
  └→ Currency → gold drop calc
HUD (UI Toolkit) → Read BuildState, TimeManager, Currency
```

### Event Bus Architecture

```
HitDetect →HitEvent→ DamageHealth →DamageDealtEvent→ VFX, Audio, ScreenShake, Adapter
                                     →EntityDiedEvent→ LevelUp, Currency, VFX, Audio, Lore
GState →GameStateChanged→ Input (map switch), Time (scale), Scene (load), Audio, HUD, EnemyAI
WorldState →ZoneRestoredEvent→ VFX (color sweep), Audio (restoration)
LevelUp →LevelUpEvent→ RuneDraft (trigger draft)
```

### Save/Load Path

```
SAVE: RunCompletion (Victory/Defeat) → SaveService → .tmp → hash → .save
AUTOSAVE: HeroCamp entry → LoadPersistentAsync()
SERVER SYNC: ProfileSyncService polls dirty flag (100ms debounce) → WebSocket
LOAD: Account.AutoLogin() + SaveService.LoadPersistentAsync() (parallel) → merge → dispatch
```

### Initialization Order

```
1. Unity Runtime Init
2. VContainer AppScope: IBackendService, INetworkManager
3. TinyRiftScope:
   ├─ Foundation (order-independent): GState, EventBus, Time, SkillRegistry, Input, HitDetect, Pool
   ├─ Core: Save, Account, ZoneDef, WorldState, Audio, VFX, Currency, Lore, StatusFX
   ├─ Feature: DamageHealth, Orbit, Burst, LevelUp, Draft, EnemyAI, WaveSpawn, Boss, Shake, Camp, Build
   └─ Presentation: HUD, DraftUI, CampUI, Codex, Adapter, Loading, RunComplete
4. GState → Menu
5. NetworkManager.ConnectAsync() (non-blocking)
6. SaveService.LoadPersistentAsync() (cached-first UI)
```

## API Boundaries

### IEventBus — cross-cutting publish/subscribe
```csharp
public interface IEventBus {
    void Publish<T>(in T eventData) where T : struct;
    IDisposable Subscribe<T>(Action<T> handler) where T : struct;
    IDisposable Subscribe<T>(object subscriber, Action<T> handler) where T : struct;
    void UnsubscribeAll(object subscriber);
    void Clear();
}
// Sync dispatch, per-subscriber try/catch, reentrancy guard (max depth 16)
```

### IGameStateManager — state machine
```csharp
public interface IGameStateManager {
    GameState CurrentState { get; }
    bool IsBossActive { get; }
    bool TransitionTo(GameState newState, GameStateContext context = default);
    void SetBossActive(bool active);
}
// Invalid transitions rejected (return false); same-state is no-op
```

### ITimeManager — time authority
```csharp
public interface ITimeManager {
    float RunElapsedTime { get; }
    float TimeScale { get; }
    void RegisterCooldown(string id, float duration);
    bool IsReady(string id);
    void ResetCooldown(string id, float duration);
    void TriggerHitStop(float duration, float timeScale = 0f);
}
// Sole owner of Time.timeScale; pause preserves pre-pause scale
```

### IBuildStateService — per-run loadout
```csharp
public interface IBuildStateService {
    IReadOnlyList<SkillInstance> OrbitSkills { get; }
    IReadOnlyList<SkillInstance> BurstSkills { get; }
    void AddSkill(string skillId);
    void UpgradeSkill(int index);
    bool HasSkill(string skillId);
    void Clear();
}
// Max 5 orbit (FIFO), 2 burst slots (fixed)
```

**Layer boundary rules:**
- Presentation → Feature: Event Bus only (subscribe to game events)
- Presentation → Foundation: Read-only interface queries (never write)
- Feature → Core: Direct interface calls + Event Bus (bidirectional)
- Core → Foundation: Direct interface calls (never Event Bus upstream)
- Foundation: No upstream dependencies

## ADR Audit

**6 ADRs exist and are Accepted.** All Foundation-layer decisions covered:
- `ADR-001`: VContainer DI Architecture & Service Registration
- `ADR-002`: Event Bus Contract & Message Type Catalogue
- `ADR-003`: Input System & InputRouter Wrapper Pattern
- `ADR-004`: Time System & Hit-Stop Ownership
- `ADR-005`: Object Pooling Strategy
- `ADR-006`: Save/Profile Serialization & Merge Strategy (Core layer)

150 technical requirements (35 systems) — 6 ADRs accepted, 144 open spaces. Feature-layer ADRs (Damage Pipeline, Orbit/Burst Combat, Rune Draft, Enemy AI, Wave Spawning) deferred until Foundation/Core coding is underway.

## Required ADRs

### ✅ Completed — Foundation & Core:
1. `docs/architecture/adr-001-vcontainer-di-architecture.md` ✅ Accepted
   Covers: Foundation module wiring, lifetime scopes. TRs: gstate-001, pooling-005, skilldata-003, eventbus-005, network-001
2. `docs/architecture/adr-002-event-bus-contract.md` ✅ Accepted
   Covers: Event type definitions, AOT safety, reentrancy guard. TRs: eventbus-001–005, gstate-002, hitdetect-002
3. `docs/architecture/adr-003-input-system-wrapper.md` ✅ Accepted
   Covers: Input System 1.19.0 wrapping, action maps, device handling. TRs: input-001–005, burst-002
4. `docs/architecture/adr-004-time-system.md` ✅ Accepted
   Covers: Time.timeScale authority, cooldown registry, pause-safe timing. TRs: time-001–005, screenshake-003, runedraft-003
5. `docs/architecture/adr-005-object-pooling.md` ✅ Accepted
   Covers: PoolProfile config, IPoolable lifecycle, IL2CPP AOT. TRs: pooling-001–005
6. `docs/architecture/adr-006-save-profile-serialization.md` ✅ Accepted
   Covers: JSON schema, atomic writes, conflict resolution. TRs: save-001–008, account-003–004

### Should have before Feature-layer implementation:
7. `/architecture-decision "Damage Pipeline & Elemental Weakness Formula"`
   TRs: dmghealth-001–005, statusfx-001–004
8. `/architecture-decision "Orbit Combat & Targeting Priority"`
   TRs: orbit-001–005
9. `/architecture-decision "Burst Skill Cooldown & Aim Resolution"`
   TRs: burst-001–004
10. `/architecture-decision "Rune Draft Rarity & Upgrade Model"`
    TRs: runedraft-001–005, levelup-001–004
11. `/architecture-decision "Enemy AI State Machine Architecture"`
    TRs: enemyai-001–004
12. `/architecture-decision "Wave Spawning & Escalation Curve"`
    TRs: wavespawn-001–004

### Can defer to implementation:
13. UI Toolkit Runtime UI Pattern (framework choice made, detail deferred)
14. Screen Shake Profile Definitions
15. Loading/Transition Animation Sequences

## Architecture Principles

1. **Strict layer isolation** — Each layer depends only on layers below. Presentation never calls Feature directly — always through Event Bus or interface queries. Violation is a blocking code review finding.
2. **Event Bus as the nervous system** — All cross-system communication goes through typed Event Bus events. Systems never hold direct references to each other. One broken subscriber never kills the bus.
3. **Data-only boundary at Foundation** — Skill Data System uses string keys (not object references) for cross-system references. Foundation layer never references gameplay types.
4. **Server-authoritative economy** — Currency balances are calculated server-side from delta reports. Client never has the authority to set its own balance.
5. **Template boundary** — All custom code lives in `Assets/_TinyRift/`. Template code in `Assets/BulletHellTemplate/` is never modified. Wrapping and bridge patterns only.
6. **AOT safety first** — Every generic type used at runtime (`ObjectPool<T>`, `Action<T>`) must have explicit AOT preservation. No reliance on runtime code generation.

## Resolved Questions

| ID | Summary | Priority | Resolution |
|----|---------|----------|------------|
| QQ-01 | Should `HeroCamp` have sub-states for upgrade/codex menus? | Low | **Closed** — UX spec (hero-camp.md) defines Camp Menu as a modal overlay with tab bar (Upgrades/Map/Codex). No sub-states needed; tabs handle content switching. |
| QQ-02 | Event Bus profiling threshold for "slow handler" warning | Low | **Closed** — Deferred to implementation profiling. No design decision required. |
| QQ-03 | Should `Clear()` be automatic on scene load or explicit per scope? | Medium | **Closed** — ADR-001 confirmed explicit `Clear()` per-scope in VContainer. Scene Manager calls `PoolManager.ClearAll()` explicitly (ADR-005). |
| QQ-04 | Inheritance vs component model for SkillDefinition (Orbit vs Burst fields) | Medium | **Closed** — ADR-002 event catalogue and Skill Data GDD use a single `SkillDefinition` ScriptableObject with both field sets, validated via `OnValidate` (zero non-applicable fields enforced per type). |
| QQ-05 | Per-skill vs per-type PresentationProfile sharing | Low | **Closed** — SkillPresentationAdapter GDD defines key-based lookup (`PresentationProfileKey` in SkillDefinition), allowing both per-skill and shared profiles at runtime without design-time commitment. |
