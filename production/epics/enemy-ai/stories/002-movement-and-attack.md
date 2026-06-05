# Story 002: Movement & Attack Integration

- **Epic**: Enemy AI
- **System**: Enemy AI — Movement & Attack
- **Type**: Integration
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-05

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-enemyai-006` | State machine architecture — movement routing via MonsterMovement | ✅ ADR-001 |
| `TR-enemyai-008` | Attack resolution — attack component integration via CharacterAttackComponent | ✅ ADR-001 |
| `TR-hitdetect-007` | Faction-aware hitbox/hurtbox registration on spawn | ✅ ADR-001 |
| `TR-hitdetect-008` | Hitbox/Hurtbox MonoBehaviours register on Start, unregister on OnDestroy | ✅ ADR-001 |
| `TR-dmghealth-001` / `TR-dmghealth-003` | Enemy death via HealthComponent — governed by DH-001 architecture | ✅ DH-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- EnemyConfig SO registered as resource, not via VContainer
- EnemyChaseAI receives references via GetComponent or inspector assignment

## Control Manifest Rules

- Never modify `Assets/BulletHellTemplate/` vendor code
- Subscribe in Awake/Start, use method groups, dispose in OnDestroy (ADR-002)
- No closure lambdas in Event Bus Subscribe calls
- Follow PascalCase naming, `_camelCase` private fields
- All Enemy AI code in `Assets/_TinyRift/Runtime/EnemyAI/`
- Test files in `Assets/_TinyRift/Tests/PlayMode/EnemyAI/`

## Description

Integrates the EnemyChaseAI state machine with the template's existing movement and attack components. Sets up the enemy prefab with MonsterMovement + EnemyChaseAI wired together, and registers hitbox/hurtbox for hit detection. Does not modify template code — only configures/extends.

## Design

### Enemy Prefab Setup

```
Enemy GameObject
├── MonsterMovement (template) — handles NavMesh/pathfinding
├── CharacterAttackComponent (template) — fires skills/projectiles
├── EnemyChaseAI (custom) — state machine referencing both
├── Collider (trigger) — registered as IHurtbox
└── HealthComponent (custom, from DH-001) — handles HP
```

### Movement Integration

- `EnemyChaseAI` sets `MonsterMovement.TargetPosition` = player position during Chase state
- `MonsterMovement` handles all actual movement — no custom movement code
- Attack state sets TargetPosition = current position (stop)

### Attack Integration

- `CharacterAttackComponent` has `StartAttack()`, `StopAttack()`, etc.
- `EnemyChaseAI` calls `CharacterAttackComponent.StartAttack()` on Attack state entry
- Calls `CharacterAttackComponent.StopAttack()` on Attack state exit

## Acceptance Criteria

1. **GIVEN** an enemy in Chase state, **WHEN** player moves, **THEN** MonsterMovement.TargetPosition follows player
2. **GIVEN** an enemy in Attack state, **WHEN** Enter is called, **THEN** CharacterAttackComponent.StartAttack() called and enemy stops moving
3. **GIVEN** an enemy in Attack state, **WHEN** Exit to Chase, **THEN** CharacterAttackComponent.StopAttack() called
4. **GIVEN** an enemy with HealthComponent, **WHEN** HP reaches 0, **THEN** enemy is deactivated/destroyed and OnDeath fires

## Test Evidence Path

- `Assets/_TinyRift/Tests/PlayMode/EnemyAI/EnemyMovementAttackIntegrationTests.cs`
- PlayMode tests with spawned enemy prefabs

## Performance Budget

- **Target**: < 0.01ms per enemy per frame (minimal wrapper over template components)
- Each enemy adds O(1) Update work: one TargetPosition set + state checks
- Attack state entry/exit calls are thin wrappers over StartAttack/StopAttack
- No allocations per tick — all references cached in Awake
- If exceeded, profile MonsterMovement.TargetPosition setter (template code, not custom)

## Out of Scope

- NavMesh surface setup or baking (assumes scene has pre-baked NavMesh)
- Enemy prefab creation or authoring (assumes prefab with MonsterMovement + CharacterAttackComponent exists)
- VContainer registration of enemy services or configs
- Object pooling for enemy lifecycle (enemies instantiated directly for M1)
- Death animations, VFX, or screen shake
- Multiple behavior types (MeleeCharger only)
- Pool cleanup on scene transition

## Dependencies

- **Depends on**: EA-001 (Basic Chase AI) — state machine exists
- **Depends on**: DH-001 (Damage & Health) — HealthComponent for death

## Risks

- **MEDIUM**: Template MonsterMovement may use NavMeshAgent — requires NavMesh surface in scene

## Completion Notes
**Completed**: 2026-06-05
**Criteria**: 4/4 passing
**Deviations**: ADVISORY — EnemyHurtbox.cs created outside story scope (necessary for hit detection), CharacterAttackComponent null-guarded (prefab may not have initialized component)
**Test Evidence**: Integration — `Assets/_TinyRift/Tests/PlayMode/EnemyAI/EnemyMovementAttackIntegrationTests.cs` (5 tests)
**Code Review**: Complete (APPROVED WITH SUGGESTIONS)
