# Story 002: Hit Cooldown & Multiple Rings

> **Epic**: Orbit Combat
> **Status**: Ready
> **Layer**: Feature
> **Type**: Logic
> **Estimate**: 3h
> **Manifest Version**: 2026-06-01
> **Last Updated**: 2026-06-05

## Context

**GDD**: `design/gdd/orbit-combat-system.md`
**Requirement**: `TR-orbit-001` (targeting through cooldown), `TR-orbit-006` (new — hit cooldown, max limit)

**ADR Governing Implementation**: ADR-008: Orbit Combat & Targeting Priority
**ADR Decision Summary**: Per-projectile `Dictionary<Collider, float>` for hit cooldown. Multiple independent `OrbitRing` instances. Max 5 rings with FIFO replacement.

**Engine**: Unity 6000.3.11f1 | **Risk**: LOW
**Engine Notes**: Ensure `OnDespawned()` clears cooldown dictionary to prevent `Collider` key leaks from destroyed enemies. Lazy null-key check on each `OnTriggerEnter`.

**Control Manifest Rules (this layer)**:
- Required: Interface-first registration (ADR-001). Event Bus for cross-system communication (ADR-002).
- Forbidden: Closure lambdas in Subscribe calls. Template code modification.
- Guardrail: Cooldown tracking < 100 entries per projectile (~32 bytes each). Per-projectile cooldown map < ~160KB peak for worst-case 4000 entries.

---

## Acceptance Criteria

*From GDD `design/gdd/orbit-combat-system.md`, scoped to this story:*

- [ ] AC 6: Per-enemy hit cooldown prevents rapid re-hits — Same projectile cannot hit the same enemy more than once per 0.3s.
- [ ] AC 7: Multiple orbit skills stack — Each drafted orbit skill creates its own independent ring. All rings update simultaneously.
- [ ] AC 11: Max orbit limit enforced — If the number of orbit skills exceeds the max (5), the oldest ring is removed.

---

## Implementation Notes

*Derived from ADR-008:*

- **Per-enemy hit cooldown**: Add `Dictionary<Collider, float>` to `OrbitProjectile`. Key = enemy collider, value = next allowed hit time (unscaled). On `OnTriggerEnter`, check if `Time.unscaledTime >= dictionary[collider]`. If yes, publish `HitEvent` and update entry to `Time.unscaledTime + 0.3f`. If no, skip.
- **Cleanup**: `OnDespawned()` clears dictionary entirely. Lazy null check in `OnTriggerEnter` — if `collider == null` or destroyed, remove key and skip.
- **Multiple rings**: `OrbitCombatService` holds `List<OrbitRing>`. Each `SpawnOrbit()` call appends new ring. `LateUpdate()` iterates all rings. Rings are independent — no collision between orbit projectiles from different rings.
- **Max limit**: Configurable via `_maxOrbitSkills` field (default 5). On `SpawnOrbit()`, if `ActiveRings.Count >= _maxOrbitSkills`, remove oldest ring (`RemoveOrbit(ActiveRings[0].SkillId)`) before adding new one.
- `RemoveOrbit(skillId)`: despawns all projectiles in the ring (returns to pool), removes ring from list. Hit cooldown maps discarded.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- ORBIT-001: Orbit ring creation, rotation, player-follow, basic hit detection (without cooldown)
- ORBIT-003: Real-time upgrade responses to projectile count/speed/radius
- ORBIT-004: Zone transition lifecycle (clear/respawn), build state integration

---

## QA Test Cases

- **AC-6**: Per-enemy cooldown prevents rapid re-hits
  - Given: Active orbit projectile, enemy collider within trigger range
  - When: `OnTriggerEnter` fires at t=0 (hit), then again at t=0.1
  - Then: Hit at t=0 publishes `HitEvent`. Hit at t=0.1 is suppressed (cooldown active)
  - When: `OnTriggerEnter` fires at t=0.35
  - Then: Hit publishes (cooldown expired)
  - Edge cases: Two different enemies hit same projectile simultaneously — both hits apply (separate cooldown entries). Enemy destroyed mid-cooldown — null key removed on next check.

- **AC-7**: Multiple orbit skills stack independently
  - Given: `SpawnOrbit("fire_orb")` creates ring A at angle θ_A
  - When: `SpawnOrbit("ice_shard")` creates ring B at angle θ_B
  - Then: `ActiveRings.Count == 2`. Ring A projectiles rotate independently from Ring B. Both rings update in same LateUpdate.
  - Edge cases: Same skill drafted twice — both instances active. Rings with same radius overlap visually but don't interact.

- **AC-11**: Max orbit limit enforced (FIFO)
  - Given: 5 active orbit rings (max = 5), ring[0] is oldest
  - When: `SpawnOrbit("new_skill")` called
  - Then: Ring[0] is removed (projectiles returned to pool), new ring appended. `ActiveRings.Count == 5`.
  - Edge cases: Limit = 3, 3 rings active, remove oldest is ring[0]. Zero rings active — no removal, just append.

---

## Test Evidence

**Story Type**: Logic
**Required evidence**: `tests/EditMode/OrbitCombat/HitCooldownMultipleRingTests.cs` — must exist and pass
**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: ORBIT-001 (Orbit Ring Core — needs spawned rings and projectiles)
- Unlocks: ORBIT-004 (needs multiple rings for lifecycle testing)
