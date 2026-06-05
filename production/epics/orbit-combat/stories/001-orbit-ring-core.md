# Story 001: Orbit Ring Core

> **Epic**: Orbit Combat
> **Status**: Ready
> **Layer**: Feature
> **Type**: Logic
> **Estimate**: 4h
> **Manifest Version**: 2026-06-01
> **Last Updated**: 2026-06-05 (in progress)

## Context

**GDD**: `design/gdd/orbit-combat-system.md`
**Requirement**: `TR-orbit-001`, `TR-orbit-002`, `TR-orbit-003`

**ADR Governing Implementation**: ADR-008: Orbit Combat & Targeting Priority
**ADR Decision Summary**: Hybrid service + pooled component. `IOrbitCombatService` manages `OrbitRing` lifecycles in LateUpdate. `OrbitProjectile` (pooled) handles trigger collider + positioning. Contact-based targeting (no active cursor).

**Engine**: Unity 6000.3.11f1 | **Risk**: LOW
**Engine Notes**: No post-cutoff APIs used. Trigger colliders, LateUpdate, ObjectPool<T> all standard. Ensure `OnDespawned()` clears hit cooldown map to prevent stale `Collider` keys from destroyed objects.

**Control Manifest Rules (this layer)**:
- Required: Interface-first — `IOrbitCombatService` registered as singleton in TinyRiftScope (ADR-001). `OrbitProjectile` implements `IPoolable` (ADR-005). Cooldown IDs prefixed `"orbit_"` (ADR-004).
- Forbidden: Service Locator, Singleton<T>, template code modification, closure lambdas in Event Bus Subscribe.
- Guardrail: Object pool Get/Return < 0.01ms per call. Orbit update < 0.05ms per frame.

---

## Acceptance Criteria

*From GDD `design/gdd/orbit-combat-system.md`, scoped to this story:*

- [ ] AC 1: Orbit spawns on draft — When an orbit skill is drafted, `OrbitRing` is created with `ProjectileCount` projectiles evenly spaced at `OrbitRadius`.
- [ ] AC 2: Orbit rotates continuously — Each frame, orbit projectiles rotate around the player at `OrbitSpeed` degrees/sec.
- [ ] AC 3: Orbit follows player position — Projectile positions update with player movement, maintaining `OrbitRadius`.
- [ ] AC 4: Orbit hits enemies on contact — When an orbit projectile's collider touches an enemy, `HitEvent` is published.
- [ ] AC 5: Projectile is not consumed on hit — After hitting an enemy, the projectile continues its orbit rotation.

---

## Implementation Notes

*Derived from ADR-008:*

- Create `IOrbitCombatService` interface + `OrbitCombatService` concrete class. Register as singleton in TinyRiftScope.
- `OrbitCombatService` manages `List<OrbitRing>`. Each `OrbitRing` is a plain C# struct with `SkillId`, `SkillDefinition` ref, `ProjectileCount`, `OrbitSpeed`, `OrbitRadius`, `CurrentAngle`, `List<OrbitProjectile>`.
- `OrbitCombatService.SpawnOrbit(skillId, playerTransform)`: create `OrbitRing`, compute initial angles, instantiate pooled `OrbitProjectile` instances, position evenly around player.
- `OrbitCombatService.LateUpdate()`: for each active ring, advance `CurrentAngle += OrbitSpeed * Time.deltaTime`, compute positions as `playerPos + (cos(angle), sin(angle)) * OrbitRadius`, set `projectile.transform.position`.
- Create `OrbitProjectile` MonoBehaviour with `SphereCollider` (isTrigger = true) on physics layer "OrbitProjectile". Implement `IPoolable`. On `OnTriggerEnter` with enemy-layer collider, check ADR-005 pool lifecycle (pooled, not consumed). Publish `HitEvent` via `ISubscriber`/`IEventBus`.
- Projectiles NOT consumed on hit. `OnTriggerEnter` publishes event but does not return projectile to pool.
- Subscribe to `SkillDraftedEvent` to trigger `SpawnOrbit()`.
- Position via direct `transform.position` in LateUpdate (no Rigidbody — purely kinematic per ADR-008 API decision).

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- ORBIT-002: Per-enemy hit cooldown (0.3s), multiple ring stack management, max orbit FIFO limit
- ORBIT-003: Real-time upgrade responses (projectile count, speed, radius changes)
- ORBIT-004: Zone transition lifecycle (clear/respawn), orbit removal despawn

---

## QA Test Cases

- **AC-1**: Orbit spawns with correct projectile count
  - Given: `IOrbitCombatService` with no active rings
  - When: `SpawnOrbit("fire_orb", playerTransform)` called with `SkillDefinition.ProjectileCount = 3, OrbitRadius = 2.5`
  - Then: `ActiveRings.Count == 1`, ring has 3 projectiles, each positioned 120° apart at radius 2.5 from player center
  - Edge cases: ProjectileCount = 0 (ring created, 0 projectiles — warning logged)

- **AC-2**: Orbit advances current angle each frame
  - Given: Active orbit ring with OrbitSpeed = 90 (deg/sec), fixed timestep
  - When: `LateUpdate()` called once at Time.deltaTime = 0.016
  - Then: `CurrentAngle` advanced by ~1.44 degrees
  - Edge cases: OrbitSpeed = 0 (no rotation — stationary minefield)

- **AC-3**: Orbit follows player position
  - Given: Active orbit ring with projectiles at known positions
  - When: Player moves from (0,0,0) to (5,0,3)
  - Then: Each projectile position is offset by (5,0,3) from previous position, radius maintained
  - Edge cases: Player teleports (large delta) — ring maintains radius, no visual pop

- **AC-4**: Hit published on enemy trigger contact
  - Given: Active orbit ring with projectile at known position, enemy collider in range
  - When: Physics frame triggers `OnTriggerEnter` on OrbitProjectile with enemy collider
  - Then: `HitEvent` published via Event Bus with correct `AttackerId`, `TargetId`, `DamageValue`
  - Edge cases: Same-faction collision → no event. Collider without registry entry → no event, no exception

- **AC-5**: Projectile persists after hit
  - Given: AC-4 has triggered (hit published)
  - When: Next LateUpdate frame
  - Then: Projectile still in ring, still positioned and rotating
  - Edge cases: Multiple consecutive frames of OnTriggerEnter (continuous contact) — event fires each frame (cooldown handled by ORBIT-002)

---

## Test Evidence

**Story Type**: Logic
**Required evidence**: `tests/EditMode/OrbitCombat/OrbitRingCoreTests.cs` — must exist and pass
**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: None (first story in epic)
- Unlocks: ORBIT-002 (Hit Cooldown & Multiple Rings), ORBIT-003 (Upgrades), ORBIT-004 (Lifecycle)
