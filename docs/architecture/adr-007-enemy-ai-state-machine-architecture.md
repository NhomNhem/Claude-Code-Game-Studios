# ADR-007: Enemy AI State Machine Architecture

## Status

Proposed

## Date

2026-06-05

## Engine Compatibility

| Field | Value |
|-------|-------|
| **Engine** | Unity 6000.3.11f1 (Unity 6 Update 3) |
| **Domain** | Gameplay (AI/State Machines) |
| **Knowledge Risk** | LOW — Enemy AI uses standard Unity APIs (MonoBehaviour, ScriptableObject, Transform) that are stable in Unity 6000.3.11f1 |
| **References Consulted** | `docs/engine-reference/unity/VERSION.md`, Enemy AI GDD (`design/gdd/enemy-ai-system.md`) |
| **Post-Cutoff APIs Used** | None — Uses MonoBehaviour, ScriptableObject, Transform (stable across Unity versions) |
| **Verification Required** | None |

## ADR Dependencies

| Field | Value |
|-------|-------|
| **Depends On** | ADR-001 (VContainer DI), ADR-002 (Event Bus), ADR-004 (Time System), ADR-005 (Object Pooling) |
| **Enables** | Wave Spawning System, Boss Encounter System |
| **Blocks** | Enemy AI stories (EA-001 Basic Chase AI, subsequent Enemy AI stories) |
| **Ordering Note** | Must be Accepted before any Enemy AI story implementation. Foundation ADRs (001-006) must be Accepted first. |

## Context

### Problem Statement

The Enemy AI System requires a state machine architecture that supports multiple behavior types (MeleeCharger, RangedCaster, SuicideBomber, Orbiter, Turret), elemental affinity with weakness/resistance tables, rift origin tracking, and wave integration. The architecture must respect existing constraints: VContainer DI for service registration, Event Bus for cross-system communication, Object Pooling for enemy lifecycle, and Time System for cooldown tracking. Without a clear architectural decision, Enemy AI implementation risks inconsistent patterns, tight coupling to template code, or violation of established architectural stances.

### Constraints

- **Template boundary**: Never modify `Assets/BulletHellTemplate/` code. Use wrapping or bridge patterns.
- **DI requirement**: All custom systems must register as interface singletons in TinyRiftScope (ADR-001).
- **Event Bus requirement**: All cross-system communication must use typed Event Bus events (ADR-002).
- **Object Pooling**: Enemies must be pooled via PoolManager (ADR-005).
- **Time System**: Attack cooldowns must use ITimerService (ADR-004).
- **Performance**: AI updates must run efficiently with 50+ active enemies on screen.

### Requirements

- Must support 5 behavior types (MeleeCharger, RangedCaster, SuicideBomber, Orbiter, Turret)
- Must support elemental affinity with weakness/resistance multipliers
- Must support rift origin tracking for visual tells
- Must integrate with Wave Spawning for pool activation/deactivation
- Must respond to GameStateChangedEvent for cleanup and boss arena clearing
- Must use Event Bus for HitEvent and EntityDiedEvent publishing
- Must use ITimerService for attack cooldown tracking
- Must be data-driven via EnemyDefinition ScriptableObject

## Decision

**Hybrid approach**: MonoBehaviour per enemy for state machine execution, with service-driven coordination for cross-cutting concerns.

### Architecture Diagram

```
TinyRiftScope (VContainer)
  └── IEnemyAIService → EnemyAIService (singleton service)
       ├── Updates all active enemies each frame
       ├── Manages enemy pool lifecycle
       └── Publishes enemy lifecycle events

Enemy Prefab (pooled via PoolManager)
  └── EnemyChaseAI (MonoBehaviour)
       ├── EnemyDefinition SO reference
       ├── EnemyAIState (enum-based state)
       ├── References: player Transform, MonsterMovement, CharacterAttackComponent
       └── Subscribes to GameStateChangedEvent

State Machine (per enemy):
  Spawn → Idle → Chase → Attack → Flee → Death
```

### Key Interfaces

```csharp
public interface IEnemyAIService
{
    void RegisterEnemy(EnemyChaseAI enemy);
    void UnregisterEnemy(EnemyChaseAI enemy);
    void UpdateAllEnemies(float deltaTime);
    void DeactivateAllEnemies();
    void DeactivateNonBossEnemies();
}

public enum EnemyAIState
{
    Spawn,
    Idle,
    Chase,
    Attack,
    Flee,
    Death
}

public class EnemyDefinition : ScriptableObject
{
    public float maxHealth;
    public float moveSpeed;
    public float damage;
    public int xpValue;
    public EnemyBehaviorType behaviorType;
    public ElementType element;
    public RiftOrigin riftOrigin;
    public Dictionary<ElementType, float> weaknessTable;
    public Dictionary<ElementType, float> resistanceTable;
    public float aggroRange;
    public float attackRange;
    public float attackCooldown;
}

public class EnemyChaseAI : MonoBehaviour
{
    public EnemyDefinition config;
    private EnemyAIState currentState;
    private Transform player;
    private MonsterMovement movement;
    private CharacterAttackComponent attack;
    private IEnemyAIService enemyService;
    private ITimeManager timeManager;
    private IEventBus eventBus;
}
```

### State Machine Implementation

Each enemy runs its own state machine in `Update()`:

- **Spawn**: Play spawn VFX, 0.5s invulnerability, transition to Idle
- **Idle**: Wander toward random point, check aggro range, transition to Chase if player detected
- **Chase**: Move toward player at config.moveSpeed, check attack range, transition to Attack if in range
- **Attack**: Stop movement, execute attack pattern, respect cooldown via ITimerService, transition to Chase after cooldown
- **Flee**: Move away from player at 1.5x moveSpeed if HP < flee threshold, transition to Chase after 3s
- **Death**: Publish EntityDiedEvent, return to pool

### Service Coordination

`EnemyAIService` provides:
- Central registration of all active enemies
- Frame-driven update loop (calls `UpdateAI()` on each registered enemy)
- Pool lifecycle coordination with Wave Spawning
- GameStateChangedEvent subscription for cleanup

### Event Bus Integration

- **Publish**: `HitEvent` (melee contact), `EntityDiedEvent` (death)
- **Subscribe**: `GameStateChangedEvent` (cleanup on zone transition/boss active)

### Elemental Affinity

Damage calculation applies multipliers from EnemyDefinition:
```csharp
float CalculateDamage(float baseDamage, ElementType attackerElement, ElementType defenderElement)
{
    float multiplier = 1.0f;
    if (config.resistanceTable.ContainsKey(defenderElement))
        multiplier *= config.resistanceTable[defenderElement];
    if (config.weaknessTable.ContainsKey(defenderElement))
        multiplier *= config.weaknessTable[defenderElement];
    return baseDamage * multiplier;
}
```

## Alternatives Considered

### Alternative 1: MonoBehaviour-only (no service)
- **Description**: Each enemy manages its own state machine independently with no central service coordination
- **Pros**: Simple, Unity-native, no service overhead
- **Cons**: No central enemy registry for Wave Spawning, no frame-level coordination, harder to enforce architectural patterns
- **Rejection Reason**: Wave Spawning requires a central enemy registry for pool activation/deactivation. Service coordination provides cleaner separation of concerns.

### Alternative 2: Centralized service-only (no MonoBehaviour per enemy)
- **Description**: EnemyAIService owns all enemy state and updates all enemies in a single loop
- **Pros**: Centralized control, easier to enforce patterns, no per-MonoBehaviour overhead
- **Cons**: Complex to manage per-enemy state in a single service, harder to leverage Unity's scene hierarchy, template integration becomes difficult
- **Rejection Reason**: Template's MonsterMovement and CharacterAttackComponent are MonoBehaviour-based. Not using MonoBehaviour per enemy would require rewriting template components or complex bridge patterns.

### Alternative 3: Pure ECS (DOTS)
- **Description**: Use Unity DOTS Entities for all enemy AI
- **Pros**: High performance with 100+ enemies, data-oriented design
- **Cons**: High learning curve, template not DOTS-based, requires significant refactoring of template systems, post-cutoff risk (Entities 1.0+ major overhaul)
- **Rejection Reason**: Template is MonoBehaviour-based. DOTS would require rewriting template components and is high-risk for MVP timeline. MonoBehaviour approach is sufficient for 50-100 enemies.

## Consequences

### Positive

- Hybrid approach balances Unity-friendly MonoBehaviour state management with service-driven coordination
- Respects all existing architectural stances (VContainer DI, Event Bus, Object Pooling, Time System)
- Clean separation: per-enemy state in MonoBehaviour, cross-cutting concerns in service
- Data-driven via EnemyDefinition ScriptableObject (designer-friendly)
- Easy to extend with new behavior types by adding enum values and state logic

### Negative

- Service coordination adds slight overhead (one service update loop + per-enemy MonoBehaviour updates)
- Requires manual registration/unregistration of enemies with EnemyAIService
- State machine logic distributed across MonoBehaviour classes (harder to see all states at once)

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Performance bottleneck with 100+ enemies | Medium | Medium | Profile EnemyAIService.UpdateAllEnemies() with 100 enemies; if >2ms, consider batch processing or job system |
| Enemy registration/deregistration bugs (leaked references) | Medium | High | EnemyAIService validates registration on Unregister; add defensive null checks in UpdateAllEnemies |
| State machine complexity grows with new behavior types | Low | Medium | Keep state machine simple (enum-based, switch statement); complex behavior delegated to behavior-specific helper methods |
| Template MonsterMovement conflicts with custom AI | Low | Medium | Use template MonsterMovement as-is; don't replace. Custom AI only controls when to call movement, not how movement works |

## GDD Requirements Addressed

| GDD System | Requirement | How This ADR Addresses It |
|------------|-------------|--------------------------|
| enemy-ai-system.md | IEnemyAIService interface injected via VContainer in TinyRiftScope | IEnemyAIService registered as singleton in TinyRiftScope (ADR-001 compliance) |
| enemy-ai-system.md | EnemyAIService updates active enemies each frame, drives state machines | EnemyAIService.UpdateAllEnemies() calls UpdateAI() on each registered enemy |
| enemy-ai-system.md | EnemyAIState per-enemy state with Update() returning current state | EnemyChaseAI MonoBehaviour with EnemyAIState enum and Update() implementation |
| enemy-ai-system.md | EnemyDefinition ScriptableObject with HP, movespeed, damage, XP value, behavior type, attack pattern, element, rift origin, elemental weakness/resistance tables | EnemyDefinition ScriptableObject with all required fields |
| enemy-ai-system.md | Elemental affinity system (fire/ice/lightning with weakness/resistance multipliers) | CalculateDamage() method applies weakness/resistance tables from EnemyDefinition |
| enemy-ai-system.md | Rift origin field in EnemyDefinition with zone assignment | RiftOrigin enum field in EnemyDefinition, used for spawn VFX color flash |
| enemy-ai-system.md | State machine architecture (Spawn → Idle → Chase → Attack → Flee → Death) | EnemyAIState enum with state transition logic in Update() |
| enemy-ai-system.md | Behavior types (MeleeCharger, RangedCaster, SuicideBomber, Orbiter, Turret) | EnemyBehaviorType enum in EnemyDefinition, behavior-specific logic in state machine |
| enemy-ai-system.md | Attack resolution (melee HitEvent, ranged projectile, suicide EntityDiedEvent) | HitEvent published on melee contact, EntityDiedEvent on death, ranged via ProjectileRegistry |
| enemy-ai-system.md | Attack cooldown tracked via ITimerService | ITimerService.RegisterCooldown() and IsReady() used in Attack state |
| enemy-ai-system.md | Wave integration (enemies activated by Wave Spawning from pool) | EnemyAIService.RegisterEnemy() called on pool activation, UnregisterEnemy() on pool return |
| enemy-ai-system.md | GameStateChangedEvent handling for cleanup and boss arena clearing | EnemyAIService subscribes to GameStateChangedEvent, calls DeactivateAllEnemies() or DeactivateNonBossEnemies() |
| enemy-ai-system.md | Run-time scaling formulas for aggro range, attack cooldown, and damage | Multipliers applied in UpdateAI() based on run elapsed time from ITimeManager |

## Performance Implications

- **CPU**: EnemyAIService.UpdateAllEnemies() ~0.5ms for 50 enemies (simple loop + delegate calls). Per-enemy Update() ~0.02ms each. Total ~1.5ms for 50 enemies (within 16.6ms 60fps budget).
- **Memory**: EnemyDefinition SOs ~2KB each. 50 enemy instances ~5KB (MonoBehaviour overhead). EnemyAIService singleton ~1KB.
- **Load Time**: ScriptableObject loading is async-friendly. No impact on scene load time.
- **Network**: None (enemy AI is local-only, no network sync).

## Migration Plan

1. Create `Assets/_TinyRift/Runtime/EnemyAI/IEnemyAIService.cs` interface
2. Create `Assets/_TinyRift/Runtime/EnemyAI/EnemyAIService.cs` implementation
3. Register IEnemyAIService in TinyRiftScope (ConfigureFeature method)
4. Create `Assets/_TinyRift/Runtime/EnemyAI/EnemyChaseAI.cs` MonoBehaviour
5. Create `Assets/_TinyRift/Runtime/EnemyAI/EnemyDefinition.cs` ScriptableObject
6. Update Wave Spawning to call EnemyAIService.RegisterEnemy() on pool activation
7. Implement state machine logic in EnemyChaseAI.Update()
8. Add Event Bus subscription for GameStateChangedEvent in EnemyAIService

**Rollback plan**: If hybrid approach proves problematic, fall back to MonoBehaviour-only (remove EnemyAIService, let enemies self-manage registration via static list).

## Validation Criteria

- [ ] EnemyAIService registers as singleton in TinyRiftScope (VContainer validation)
- [ ] 50 active enemies update at 60fps without frame drops (profiling)
- [ ] State transitions work correctly (Idle → Chase → Attack → Death)
- [ ] HitEvent and EntityDiedEvent publish correctly (Event Bus validation)
- [ ] Attack cooldowns respect ITimerService (Time System validation)
- [ ] Wave Spawning can activate/deactivate enemies (pool integration)
- [ ] GameStateChangedEvent triggers cleanup (zone transition/boss active)
- [ ] Elemental affinity multipliers apply correctly (damage calculation test)

## Related Decisions

- ADR-001: VContainer DI Architecture & Service Registration (IEnemyAIService registration)
- ADR-002: Event Bus Contract & Message Type Catalogue (HitEvent, EntityDiedEvent)
- ADR-004: Time System & Hit-Stop Ownership (ITimerService for cooldowns)
- ADR-005: Object Pooling Strategy (enemy pooling via PoolManager)
- Architecture.md: Enemy AI listed in Feature layer, depends on GameState, Hit Detection, Object Pooling
