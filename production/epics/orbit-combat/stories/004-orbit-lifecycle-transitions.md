# Story 004: Orbit Lifecycle & Transitions

> **Epic**: Orbit Combat
> **Status**: Ready
> **Layer**: Feature
> **Type**: Integration
> **Estimate**: 3h
> **Manifest Version**: 2026-06-01
> **Last Updated**: 2026-06-05

## Context

**GDD**: `design/gdd/orbit-combat-system.md`
**Requirement**: `TR-orbit-003` (pool cleanup on despawn), `TR-orbit-005` (new — zone transition lifecycle)

**ADR Governing Implementation**: ADR-008: Orbit Combat & Targeting Priority
**ADR Decision Summary**: Orbits cleared on `GameStateChangedEvent` (non-InRun). Re-spawned on zone entry from `IBuildStateService.OrbitSkills`. `RemoveOrbit()` returns all projectiles to pool. PoolManager calls `ClearAll()` at scene transition boundary.

**Engine**: Unity 6000.3.11f1 | **Risk**: LOW
**Engine Notes**: PoolManager.ClearAll() called by SceneManager on transition (ADR-005). Orbit rings must also be cleared before PoolManager clears, or dangling references cause errors.

**Control Manifest Rules (this layer)**:
- Required: Event Bus for GameStateChangedEvent subscription (ADR-002). PoolManager.ClearAll() on scene transition (ADR-005). Interface injection via VContainer (ADR-001). Cooldown ID prefix `"orbit_"` (ADR-004).
- Forbidden: Direct static references to game state. Template code modification.
- Guardrail: Scene transition ClearAll (200 objects) < 1ms. Pool pre-warm for orbit projectiles per scene via PoolProfile.

---

## Acceptance Criteria

*From GDD `design/gdd/orbit-combat-system.md`, scoped to this story:*

- [ ] AC 9: Orbit cleared on zone transition — When `GameStateChangedEvent` fires with a non-`InRun` state, all orbits are destroyed.
- [ ] AC 10: Orbit re-spawned on zone entry — When entering a new zone, orbits are rebuilt from Build State's active skill list.
- [ ] AC 13: Orbit removal despawns projectiles — When `RemoveOrbit(SkillId)` is called, all projectiles for that ring are returned to pool.

---

## Implementation Notes

*Derived from ADR-008:*

- Subscribe to `GameStateChangedEvent` in `OrbitCombatService.Awake()` or `Start()` (per ADR-002: subscribe in Start, not constructor).
- On `GameStateChangedEvent` with `newState != GameState.InRun`: call `ClearAllOrbits()`. This destroys all rings and returns all projectiles to pool.
- On zone entry: `OrbitCombatService` reads `IBuildStateService.OrbitSkills` (list of active `SkillInstance`). For each orbit skill, call `SpawnOrbit(skillId, playerTransform)`.
- `RemoveOrbit(skillId)`: iterate ring's projectile list, call `PoolManager.Return(projectile)` for each, clear list, remove ring from `ActiveRings`.
- Ordering: `ClearAllOrbits()` must be called BEFORE `PoolManager.ClearAll()` at scene transition boundary. SceneManager orchestrates this — `OrbitCombatService` clears on `GameStateChangedEvent`, then SceneManager calls `PoolManager.ClearAll()`.
- `OnDespawned()` on `OrbitProjectile`: clear hit cooldown dictionary, reset visual state (scale, rotation), disable GameObject.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- ORBIT-001: Core ring creation, rotation, hit detection
- ORBIT-002: Hit cooldown management, multiple ring FIFO limits
- ORBIT-003: Real-time upgrade responses

---

## QA Test Cases

- **AC-9**: Orbits cleared on non-InRun state transition
  - Given: 3 active orbit rings with projectiles in pool
  - When: `GameStateChangedEvent` published with `GameState.HeroCamp`
  - Then: `ActiveRings` is empty. All projectiles returned to pool. Hit cooldown maps cleared.
  - Edge cases: `GameStateChangedEvent` with `GameState.InRun` (same state) — no-op. `GameStateChangedEvent` with `GameState.Paused` — clears orbits (pause exits InRun per GState design).

- **AC-10**: Orbits re-spawned on zone entry
  - Given: `IBuildStateService.OrbitSkills` returns 2 orbit skill IDs (`"fire_orb"`, `"ice_shard"`)
  - When: OrbitCombatService receives zone entry signal (inferred via GameState → InRun after transition completes)
  - Then: 2 OrbitRings created matching the skill IDs. Projectile count, radius, speed from each skill's `SkillDefinition`.
  - Edge cases: Empty Build State (no orbit skills) — no rings created, no error. Build State returns skill ID not in registry — log warning, skip.

- **AC-13**: RemoveOrbit despawns projectiles
  - Given: Active ring with 3 projectiles, pool has 5 pre-warmed instances (8 total in pool: 3 in-use, 5 free)
  - When: `RemoveOrbit("fire_orb")` called
  - Then: Ring removed from ActiveRings. Pool free count goes from 5 to 8 (3 returned). `PoolManager.Get<OrbitProjectile>()` returns fresh (non-dangling) instances.
  - Edge cases: Remove non-existent skill ID — no-op, log warning. Remove already-removed ring — no-op (ring not in ActiveRings). RemoveOrbit called during LateUpdate iteration — safe via removal from list (iterate snapshot or use reverse iteration).

---

## Test Evidence

**Story Type**: Integration
**Required evidence**: `tests/EditMode/OrbitCombat/OrbitLifecycleTests.cs` — must exist and pass
**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: ORBIT-001 (Orbit Ring Core), ORBIT-002 (Hit Cooldown & Multiple Rings)
- Unlocks: None
