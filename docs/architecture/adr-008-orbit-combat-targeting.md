# ADR-008: Orbit Combat & Targeting Priority

## Status

Accepted

## Date

2026-06-05

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3 LTS) |
| **Domain** | Core (combat gameplay) |
| **Knowledge Risk** | LOW — uses standard MonoBehaviour patterns, trigger colliders, ObjectPool<T> |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md`, `docs/engine-reference/unity/modules/physics.md`, `docs/engine-reference/unity/current-best-practices.md`, `docs/engine-reference/unity/deprecated-apis.md` |
| **Post-Cutoff APIs Used** | None |
| **Verification Required** | Orbit projectile hit cooldown map cleanup on enemy destruction; no stale `Collider` keys remain in `Dictionary<Collider, float>` |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (VContainer DI), ADR-002 (Event Bus), ADR-004 (Time System), ADR-005 (Object Pooling) |
| **Enables** | None |
| **Blocks** | Orbit Combat epic (SYS-020) — all 4 stories cannot be implemented until this ADR is Accepted |
| **Ordering Note** | Must be Accepted before `/create-stories orbit-combat` runs |

## Context

### Problem Statement

The Orbit Combat System manages passive orbit-style skills — rings of projectiles that rotate around the player and auto-hit enemies on contact. This ADR determines the architecture for orbit ring management, projectile lifecycle, targeting (trigger-contact-based, not active targeting), hit event dispatch, and integration with existing Foundation/Core infrastructure (VContainer DI, Event Bus, Object Pooling, Time System).

### Constraints

- Must follow existing VContainer DI patterns (ADR-001) — register `IOrbitCombatService` as interface singleton in TinyRiftScope
- Must use Event Bus for cross-system communication (ADR-002) — orbit hits publish `HitEvent`, orbit lifecycle responds to `GameStateChangedEvent`
- Must use `PoolManager` wrapping `UnityEngine.Pool.ObjectPool<T>` for `OrbitProjectile` pooling (ADR-005)
- Must route cooldown tracking through `ITimeManager` (ADR-004) — cooldown IDs prefixed with `"orbit_"`
- Must never modify `Assets/BulletHellTemplate/` vendor code
- Must never use Service Locator, Singleton<T>, or FindObjectOfType for cross-system resolution
- GDD specifies 13 acceptance criteria covering spawn, rotation, hit, cooldown, upgrades, lifecycle

### Requirements

- Must support passive orbital auto-attack with trigger-contact-based hit detection (no active targeting cursor/enemy selection)
- Orbit projectiles must NOT be consumed on hit — they persist and orbit continuously
- Must support per-enemy hit cooldown (0.3s default) per projectile to prevent rapid re-hits of the same target
- Must support multiple independent orbit rings (up to 5, configurable) with FIFO replacement
- Must support real-time upgrade changes to projectile count, orbit speed, orbit radius
- Must clear orbits on zone transition and re-spawn from Build State on zone entry
- Must use `ObjectPool<T>` for all `OrbitProjectile` instances — zero GC allocation on spawn/despawn
- Must handle edge cases: zero projectile count (log warning), zero speed (stationary minefield), radius clamped to 0.5m minimum

## Decision

Use a **hybrid service + pooled component** architecture:

- **`IOrbitCombatService` / `OrbitCombatService`**: Singleton service registered in TinyRiftScope. Owns the list of active `OrbitRing` instances. Handles orbit spawn/remove (triggered by Event Bus subscription to skill draft/game state events). Runs `LateUpdate()` to advance all rings' `CurrentAngle` and positions projectiles.

- **`OrbitRing`**: Plain C# runtime container (not MonoBehaviour). Holds `SkillId`, `SkillDefinition` reference, runtime parameters (`ProjectileCount`, `OrbitSpeed`, `OrbitRadius`), `CurrentAngle` accumulator, and list of pooled `OrbitProjectile` instances. Parameters are mutable — upgrades update them in real time.

- **`OrbitProjectile`**: Pooled MonoBehaviour implementing `IPoolable`. Has a `SphereCollider` (isTrigger = true) on a dedicated physics layer ("OrbitProjectile"). On `OnTriggerEnter` with an enemy-layer collider, checks per-enemy hit cooldown (`Dictionary<Collider, float>`). If not on cooldown, publishes `HitEvent` via `ISubscriber`-injected Event Bus reference. Projectile is NOT returned to pool on hit — it persists until the ring is removed.

- **Projectile positioning**: Executed in `OrbitCombatService.LateUpdate()`. Each frame, for each active `OrbitRing`:
  1. Advance `CurrentAngle += OrbitSpeed * Time.deltaTime` (degrees/sec)
  2. For each projectile at index `i`, compute: `playerPos + (cos(baseAngle + (360°/count) × i), sin(...)) × orbitRadius`
  3. Set `OrbitProjectile.transform.position` directly (no Rigidbody — purely kinematic positioning)
  4. Projectiles rotate in XZ plane (Y-up)

- **Hit detection**: Trigger-contact-based (no active targeting cursor). "Targeting priority" in this context means orbit projectiles only collide with enemy-layer colliders (enforced by physics layer matrix). The orbit automatically prioritizes nearby enemies because projectiles sweep through the arena radius — enemies close to the orbit ring path take hits first.

- **Per-enemy hit cooldown**: `Dictionary<Collider, float>` per `OrbitProjectile`. Key is the enemy's collider instance. Value is the next allowed hit time in unscaled time. Map is populated on hit, checked on `OnTriggerEnter`, cleaned up in `OnDespawned()`. To prevent dangling keys from destroyed colliders, `OnDespawned()` clears the dictionary. Additionally, a lazy cleanup pass removes null keys on each hit check.

- **Orbit lifecycle via Event Bus**:
  - `SkillDraftedEvent` (published by Rune Draft System) → `OrbitCombatService.SpawnOrbit(skillId, playerTransform)`
  - `GameStateChangedEvent` with non-`InRun` state → `OrbitCombatService.ClearAllOrbits()`
  - Zone entry: `OrbitCombatService` reads `IBuildStateService.OrbitSkills` and spawns orbits for each

- **Upgrades**: `BuildState.UpgradeSkill()` is called by Rune Draft. OrbitCombatService subscribes to `SkillUpgradedEvent` and updates the corresponding `OrbitRing` parameters in real time:
  - `ProjectileCount` increase: spawn new projectile(s) at evenly distributed angles, fade in over 0.2s
  - `ProjectileCount` decrease: remove excess projectiles (last-in-first-removed), return to pool
  - `OrbitSpeed`/`OrbitRadius`: update ring parameters immediately
  - `BaseDamage`: applied to `HitEvent` payload at publish time (projectiles don't cache damage)

### Architecture Diagram

```
Player GameObject
└─ (no orbit components on player — orbits managed by service)

TinyRiftScope (VContainer)
└─ IOrbitCombatService → OrbitCombatService (singleton)
   └─ List<OrbitRing>
      ├─ SkillId: "fire_orb"
      │  └─ OrbitProjectile[0] (pooled, trigger collider)
      │  └─ OrbitProjectile[1] (pooled, trigger collider)
      │  └─ ...
      └─ SkillId: "ice_shard"
         └─ OrbitProjectile[0] (pooled, trigger collider)
         └─ ...

Event Flow:
  SkillDraftedEvent → OrbitCombatService.SpawnOrbit()
  SkillUpgradedEvent → OrbitCombatService.UpdateOrbit()
  GameStateChangedEvent → OrbitCombatService.ClearAllOrbits()
  OrbitProjectile.OnTriggerEnter(enemy) → HitEvent → Event Bus → Damage & Health
```

### Key Interfaces

```csharp
public interface IOrbitCombatService {
    void SpawnOrbit(string skillId, Transform playerTransform);
    void RemoveOrbit(string skillId);
    void ClearAllOrbits();
    IReadOnlyList<OrbitRing> ActiveRings { get; }
}

public struct OrbitRing {
    public string SkillId { get; }
    public SkillDefinition SkillDef { get; }
    public int ProjectileCount { get; set; }
    public float OrbitSpeed { get; set; }       // degrees/sec
    public float OrbitRadius { get; set; }       // world units
    public float CurrentAngle { get; set; }      // accumulated
    public List<OrbitProjectile> Projectiles { get; }
}

public class OrbitProjectile : MonoBehaviour, IPoolable {
    // Injected via VContainer
    private ISubscriber _eventBus;
    // Runtime state
    private Dictionary<Collider, float> _hitCooldowns;
    private float _hitCooldownDuration = 0.3f;

    void OnTriggerEnter(Collider other) { /* check cooldown, publish HitEvent */ }
    void OnSpawned() { /* reset cooldown map */ }
    void OnDespawned() { /* clear cooldown map, reset state */ }
}
```

## Alternatives Considered

### Alternative 1: Pure Service Architecture
- **Description**: `OrbitCombatService` creates/repositions projectiles each frame using a single reusable set of pooled GameObjects. No per-projectile MonoBehaviour logic — service reads triggers via Physics.OverlapSphere or similar.
- **Pros**: Centralized control, no per-projectile component overhead
- **Cons**: Requires manual trigger detection via physics queries (OverlapSphere each frame, GC allocation risk). Cannot use standard Unity trigger events. More complex to manage per-projectile hit cooldowns.
- **Rejection Reason**: The per-projectile MonoBehaviour pattern is idiomatic Unity and leverages `OnTriggerEnter` which is already optimized by the engine. Physics queries in a service would duplicate what the engine does for free.

### Alternative 2: Pure Component Architecture
- **Description**: Each orbit skill is a MonoBehaviour on the player (or child) that manages its own ring independently. No central `OrbitCombatService`.
- **Pros**: Autonomous per-skill components, no service layer
- **Cons**: Inconsistent with established VContainer DI pattern (ADR-001) — components on the player cannot be registered via DI. Cannot coordinate across rings (max limit enforcement, FIFO replacement). Reading Build State from multiple components creates code duplication.
- **Rejection Reason**: Violates ADR-001 pattern by requiring component-based registration outside DI. Lacks cross-ring coordination needed for max limit + FIFO replacement + zone transition lifecycle.

## Consequences

### Positive
- Consistent with established architecture patterns (DI, Event Bus, Object Pool)
- Per-projectile `OrbitProjectile` MonoBehaviour uses standard Unity lifecycle (`OnTriggerEnter`, `LateUpdate` positioning)
- Zero GC allocation on spawn/despawn via `ObjectPool<T>`
- Event Bus decouples orbit lifecycle from Rune Draft, Build State, Game State — no circular dependencies
- Per-projectile hit cooldown maps are self-contained and cleaned up on despawn
- Upgrades modify `OrbitRing` struct parameters in real time — no re-instantiation needed

### Negative
- Orbits require `LateUpdate()` for positioning — adds a fixed update pass per active ring (trivial for ≤5 rings)
- Per-projectile `Dictionary<Collider, float>` has memory cost: ~100 enemies × 5 rings × 3-8 projectiles/ring = up to 4000 entries worst case. Each entry ~40 bytes = ~160KB peak. Acceptable for MVP.
- Orbit projectiles only hit enemies that enter their trigger radius — no "smart" targeting that selects far enemies. Intentional — the orbit is a defensive/area-denial pattern.

### Risks
- **Risk**: Destroyed enemy colliders become dangling keys in per-projectile cooldown dictionaries → hit cooldown leaks memory
  - **Mitigation**: `OnDespawned()` clears the dictionary entirely. Lazy null-key check on each `OnTriggerEnter`. Pool safety net returns projectiles to pool on `OnDisable`.
- **Risk**: If player moves very fast, orbit projectiles may briefly lag behind (LateUpdate positioning after player movement in Update)
  - **Mitigation**: GDD-specified intentional behavior — projectiles follow, not drag. The visual effect is natural (orbits trail the player slightly if they dash).

## GDD Requirements Addressed

| GDD System | Requirement | How This ADR Addresses It |
|------------|-------------|--------------------------|
| `design/gdd/orbit-combat-system.md` | TR-orbit-001: Passive orbital auto-attack with targeting priority | Contact-based targeting via trigger colliders on pooled OrbitProjectile + physics layer filtering. No active targeting cursor — "priority" = enemies along the orbit path get hit first. |
| `design/gdd/orbit-combat-system.md` | TR-orbit-002: Orbit rotation speed and projectile spawning | `OrbitRing.CurrentAngle` advanced each LateUpdate at `OrbitSpeed` deg/sec. Projectiles spawned at evenly-spaced angles on `SpawnOrbit()`. |
| `design/gdd/orbit-combat-system.md` | TR-orbit-003: Uses ObjectPool for projectile pooling | `OrbitProjectile` implements `IPoolable`. `PoolManager.Get<OrbitProjectile>()` / `Return()` via ADR-005 wrapping. |
| `design/gdd/orbit-combat-system.md` | GDD AC 6: Per-enemy hit cooldown (0.3s) | `Dictionary<Collider, float>` per OrbitProjectile. Cooldown checked on `OnTriggerEnter`, cleaned on `OnDespawned()`. |
| `design/gdd/orbit-combat-system.md` | GDD AC 7-8: Multiple orbits stack + upgrades | `IOrbitCombatService` manages `List<OrbitRing>`. Upgrade events modify ring parameters in real time. |
| `design/gdd/orbit-combat-system.md` | GDD AC 9-10: Zone transition lifecycle | `GameStateChangedEvent` subscriber clears/re-spawns orbits. Build State provides active skill list on entry. |

## Performance Implications
- **CPU**: `OrbitCombatService.LateUpdate()` — O(n × m) where n = orbit rings (≤5), m = projectiles per ring (≤8). Each iteration is 1 multiplication + 3 trig calls per projectile. < 0.05ms for worst case.
- **Memory**: Per-projectile cooldown dictionary: ~160KB worst case (4000 entries × 40 bytes). Pool pre-warm: ~40 OrbitProjectile instances × ~200 bytes each = ~8KB.
- **Load Time**: Pool pre-warm on zone entry: instantiate 40 OrbitProjectiles at pool creation. ~1-2ms one-time cost.
- **Network**: None — orbit combat is purely client-side.

## Migration Plan

This is a new system (no existing implementation to migrate). Implementation order:
1. Create `IOrbitCombatService` / `OrbitCombatService` with empty ring list
2. Create `OrbitRing` struct
3. Create `OrbitProjectile` MonoBehaviour with trigger collider, `IPoolable`
4. Register in TinyRiftScope (VContainer)
5. Subscribe to `SkillDraftedEvent`, `GameStateChangedEvent`, `SkillUpgradedEvent`
6. Implement `LateUpdate()` positioning
7. Implement hit detection + cooldown map
8. Wire zone transition lifecycle through Build State

## Validation Criteria
- Orbit spawns on skill draft with correct projectile count at correct radius
- Orbit rotates at specified speed (verified with frame-accurate time assertions in EditMode tests)
- Orbit projectiles follow player position (PlayMode integration test)
- `OnTriggerEnter` with enemy publishes `HitEvent` (unit test with mock Event Bus)
- Same projectile cannot hit same enemy more than once per 0.3s (EditMode cooldown test)
- Multiple orbit skills produce independent rings (integration test)
- Upgrade to projectile count adds/removes projectiles instantly (EditMode test)
- Zone transition clears all orbits (PlayMode test with GameStateChangedEvent)
- Zero projectile count logs warning, does not crash (unit test)
- Pool returns projectiles correctly on orbit removal (PoolManager integration test)
- All tests pass in IL2CPP build (no AOT issues)

## Related Decisions
- ADR-001: VContainer DI Architecture & Service Registration
- ADR-002: Event Bus Contract & Message Type Catalogue
- ADR-004: Time System & Hit-Stop Ownership
- ADR-005: Object Pooling Strategy
