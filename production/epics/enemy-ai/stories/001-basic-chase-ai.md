# Story 001: Basic Chase AI

- **Epic**: Enemy AI
- **System**: Enemy AI — Chase Behavior
- **Type**: Logic
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Complete
- **Last Updated**: 2026-06-05

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-enemyai-002` | Enemy detects nearest player within detection range | ✅ ADR-001 |
| `TR-enemyai-001` | Enemy moves toward detected player at configured speed | ✅ ADR-001 |
| `TR-enemyai-008` | Enemy attacks (fires ability/melee) when within attack range | ✅ ADR-002 |
| `TR-enemyai-006` | Returns to idle/patrol when player leaves detection range | ⚠️ Partial (no dedicated ADR) |
| `TR-enemyai-003` | All parameters in EnemyAIConfig SO — no hardcoded values | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `EnemyAIConfig` is a ScriptableObject loaded via VContainer or Resources
- `EnemyChaseAI` is a MonoBehaviour attached to enemy prefab

**ADR-002 (Event Bus Contract):**
- Subscribe in Awake/Start, never constructor — VContainer injection happens after construction
- Store IDisposable token from Subscribe, dispose in OnDestroy
- Use method groups, never closure lambdas
- Events are `readonly record struct` with `Event` suffix, passed by `in`

## Control Manifest Rules

Global rules apply (naming conventions, performance budgets, forbidden APIs). No Feature Layer rules exist yet for Enemy AI (see control-manifest.md §Feature Layer). Key applicable rules:
- Never modify `Assets/BulletHellTemplate/` vendor code
- Subscribe in Awake/Start, use method groups, dispose in OnDestroy (ADR-002)
- No closure lambdas in Event Bus Subscribe calls
- Follow PascalCase naming, `_camelCase` private fields

## Engine Notes

**N/A — no post-cutoff Unity 6000.3.11f1 APIs used.** All runtime dependencies (MonsterMovement, CharacterAttackComponent) are template components. Movement/attack routing goes through existing template wrappers. Standard Unity APIs only: `Transform`, `Vector3.Distance`, `GameObject.FindGameObjectsWithTag`.

## Description

Implements a basic chase AI state machine for enemies. Three states: Idle (patrol/wander), Chase (move toward player), Attack (stop and fire when in range). All configurable via `EnemyAIConfig` ScriptableObject. Uses template's `MonsterMovement` for actual movement and attacks through the template's existing `CharacterAttackComponent`.

## Design

```csharp
public enum EnemyAIState { Idle, Chase, Attack }

public class EnemyAIConfig : ScriptableObject
{
    public float detectionRange = 8f;
    public float attackRange = 2f;
    public float moveSpeed = 3.5f;
    public float idleWanderRadius = 3f;
    public float attackCooldown = 1.5f;
    public float losePlayerTime = 3f; // seconds before returning to idle
}

public class EnemyChaseAI : MonoBehaviour
{
    public EnemyAIConfig config;
    public EnemyAIState currentState { get; private set; }

    // References (assigned via inspector or VContainer)
    private Transform player;
    private MonsterMovement movement;
    private CharacterAttackComponent attack;
}
```

### State Machine

| State | Enter | Update | Exit |
|-------|-------|--------|------|
| Idle | Pick random wander point | Wander toward point; if player detected → Chase | — |
| Chase | Start moving toward player | Move toward player at config.moveSpeed; if in attackRange → Attack; if player lost for losePlayerTime → Idle | Stop moving |
| Attack | Stop movement, start attack sequence | Fire attack on cooldown; if player exits attackRange → Chase | Stop attack sequence |

### Player Detection

- Uses `GameObject.FindGameObjectsWithTag("Player")` or cached player reference
- Distance check: `Vector3.Distance(transform.position, player.position) <= config.detectionRange`
- Line-of-sight optional (deferred — basic distance check for M1)

## Acceptance Criteria

1. **GIVEN** an enemy with EnemyChaseAI, **WHEN** a player is within detection range, **THEN** state transitions from Idle to Chase, and enemy moves toward player
2. **GIVEN** an enemy in Chase state, **WHEN** within attack range, **THEN** state transitions to Attack and enemy stops moving and fires
3. **GIVEN** an enemy in Chase state, **WHEN** player moves beyond detection range for losePlayerTime, **THEN** state returns to Idle
4. **GIVEN** an enemy in Attack state, **WHEN** player moves outside attack range, **THEN** state returns to Chase
5. **GIVEN** an enemy with EnemyAIConfig SO, **WHEN** detectionRange is changed to 15, **THEN** the AI uses the new value (no hardcoding)

## QA Test Cases

- **AC1 (Idle→Chase)**: Place player within detection range. Verify state transitions to Chase, enemy moves toward player.
- **AC2 (Chase→Attack)**: Move player within attack range. Verify state transitions to Attack, enemy stops and fires.
- **AC3 (Chase→Idle)**: Move player beyond detection range for losePlayerTime. Verify state returns to Idle.
- **AC4 (Attack→Chase)**: Move player outside attack range. Verify state returns to Chase.
- **AC5 (Config SO)**: Change detectionRange to 15. Verify AI uses new value (no hardcoding).

**Edge cases**: Null player (destroyed), distance exactly at boundary, multiple enemies tracking same player.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/EnemyAI/EnemyChaseAITests.cs`
- Unit tests for state transitions with mocked player transforms

## Out of Scope

- Line-of-sight detection (distance-only for M1)
- Multiple behavior types (MeleeCharger only — RangedCaster, SuicideBomber deferred)
- Flee state (not in scope for basic chase AI)
- Patrol waypoints (random wander only, no authored paths)
- VContainer registration of EnemyAIConfig (config loaded via Resources for M1)
- Pool integration for enemy lifecycle (enemy instantiated directly for M1)
- Any UI/HUD elements (health bars, aggro indicators)

## Dependencies

- **Depends on**: Template MonsterEntity, MonsterMovement, CharacterAttackComponent
- **Unlocks**: Wave spawning with functional enemies

## Performance Budget

- **Target**: < 0.05ms per enemy per frame (Update + state machine tick)
- **Measurement**: 50 simultaneous enemies at 60 FPS = 2.5ms total AI budget (15% of frame)
- If exceeded, profile hot path (Vector3.Distance in Update) and batch distance checks
- State machine transitions are O(1) — no allocations per tick

## Risks

- **LOW**: Player may be null (destroyed) — guard with null check in Update
- **LOW**: Template movement may conflict with custom AI — use template MonsterMovement, don't replace

## Completion Notes
**Completed**: 2026-06-05
**Criteria**: 5/5 passing
**Deviations**: ADVISORY — asmdef modified (Assembly-CSharp ref added), MonsterMovementComponent used instead of CharacterAttackComponent (template reality)
**Test Evidence**: Logic — `Assets/_TinyRift/Tests/EditMode/EnemyAI/EnemyChaseAITests.cs` (20 tests)
**Code Review**: Complete (APPROVED WITH SUGGESTIONS, user accepted)
