# Story 003: Upgrades & Real-Time Changes

> **Epic**: Orbit Combat
> **Status**: Ready
> **Layer**: Feature
> **Type**: Integration
> **Estimate**: 3h
> **Manifest Version**: 2026-06-01
> **Last Updated**: 2026-06-05

## Context

**GDD**: `design/gdd/orbit-combat-system.md`
**Requirement**: `TR-orbit-002` (upgrade response), `TR-orbit-007` (new — zero count edge case)

**ADR Governing Implementation**: ADR-008: Orbit Combat & Targeting Priority
**ADR Decision Summary**: Upgrades modify `OrbitRing` parameters in real time. `ProjectileCount` changes spawn/remove projectiles. `OrbitSpeed`/`OrbitRadius` update immediately. New projectiles fade in over 0.2s. Radius clamped to 0.5m minimum.

**Engine**: Unity 6000.3.11f1 | **Risk**: LOW
**Engine Notes**: Pooled projectile instantiation on count-increase must respect pool capacity. Pre-warm pool with sufficient capacity for max possible projectiles.

**Control Manifest Rules (this layer)**:
- Required: Event Bus for cross-system communication (ADR-002). PoolManager for projectile lifecycle (ADR-005).
- Forbidden: Direct system references for cross-system events. Closure lambdas in Subscribe.
- Guardrail: Object pool Get/Return < 0.01ms per call. Pool capacity pre-warmed per scene.

---

## Acceptance Criteria

*From GDD `design/gdd/orbit-combat-system.md`, scoped to this story:*

- [ ] AC 8: Upgrade changes take effect immediately — When an upgrade modifies `ProjectileCount`, `OrbitSpeed`, or `OrbitRadius`, the orbit ring updates in real time.
- [ ] AC 12: Zero projectile count logs warning — Orbit ring with 0 projectiles logs a warning but does not crash.

---

## Implementation Notes

*Derived from ADR-008:*

- Subscribe to `SkillUpgradedEvent` (published by Rune Draft/Build State) in `OrbitCombatService`.
- On upgrade received:
  - **ProjectileCount increase**: Compute new evenly-spaced angles. For each new projectile slot, `PoolManager.Get<OrbitProjectile>()`, position at computed angle, add to ring's projectile list. Fade in over 0.2s (simple scale tween from 0 to 1).
  - **ProjectileCount decrease**: Remove excess projectiles (last-in-first-removed). `PoolManager.Return()` each removed projectile.
  - **OrbitSpeed change**: Set `OrbitRing.OrbitSpeed = newValue`.
  - **OrbitRadius change**: Set `OrbitRing.OrbitRadius = Mathf.Max(newValue, 0.5f)` (clamp to 0.5m minimum).
  - **BaseDamage**: Not cached on projectiles — `HitEvent` payload reads current damage from `SkillDefinition` at publish time.
- **Zero projectile count**: If `SkillDefinition.ProjectileCount == 0`, create `OrbitRing` with empty projectile list. Log `Debug.LogWarning($"[OrbitCombat] Skill {skillId} has 0 projectiles — ring is empty")`. Do not crash.

---

## Out of Scope

*Handled by neighbouring stories — do not implement here:*

- ORBIT-001: Core orbit ring creation, rotation, hit detection
- ORBIT-002: Hit cooldown management, multiple ring limits
- ORBIT-004: Zone transition lifecycle, build state respawn

---

## QA Test Cases

- **AC-8c**: ProjectileCount increase spawns new projectiles
  - Given: Active orbit ring with 3 projectiles at 120° spacing, CurrentAngle = 0
  - When: Upgrade increases ProjectileCount from 3 to 5
  - Then: Ring now has 5 projectiles at 72° spacing. New 2 projectiles fade in over 0.2s. Existing 3 projectiles re-positioned to match new spacing.
  - Edge cases: Increase from 0 to N — all N projectiles spawn fresh. Increase beyond pool capacity — pool grows on demand (warning logged per ADR-005).

- **AC-8s**: OrbitSpeed upgrade takes effect immediately
  - Given: Active ring with OrbitSpeed = 90 deg/sec
  - When: Upgrade changes OrbitSpeed to 180
  - Then: Next LateUpdate advances CurrentAngle by 180 × deltaTime (previously 90 × deltaTime)
  - Edge cases: OrbitSpeed = 0 → no rotation (valid minefield). OrbitSpeed = negative → absolute value (clamped to positive).

- **AC-8r**: OrbitRadius upgrade updates immediately
  - Given: Active ring with OrbitRadius = 2.5
  - When: Upgrade changes OrbitRadius to 4.0
  - Then: All projectiles instantly re-position to radius 4.0 from player center
  - Edge cases: Radius < 0.5 → clamped to 0.5. Radius = 0 (clamped) → projectiles at minimum distance from player.

- **AC-12**: Zero projectile count logs warning
  - Given: `SpawnOrbit()` with `SkillDefinition.ProjectileCount = 0`
  - Then: Ring created with empty projectile list. `Debug.LogWarning` called with message containing skill ID.
  - Edge cases: Zero-count ring upgraded to N — spawns N projectiles. N-count ring upgraded to 0 — removes all projectiles, warning logged.

---

## Test Evidence

**Story Type**: Integration
**Required evidence**: `tests/EditMode/OrbitCombat/OrbitUpgradeTests.cs` — must exist and pass
**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: ORBIT-001 (Orbit Ring Core — needs spawned rings and projectiles)
- Unlocks: None
