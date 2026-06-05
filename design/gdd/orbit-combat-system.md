# Orbit Combat System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (environmental ground traces added for P1)
> **Status**: Designed

> **System ID**: #20
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 18 (Foundation → Core → Feature → Presentation → Polish)
> **Depends on**: Skill Data System (#3), Damage & Health (#19), Hit Detection (#8), Object Pooling (#4)
> **Depended by**: Build State (#29), HUD (#30)

## 1. Overview

The Orbit Combat System manages passive orbit-style skills — projectiles that rotate around the player and auto-hit enemies on contact. Each orbit skill is a ring of projectiles spinning at a fixed speed and radius. Orbits activate on draft (no cooldown, no mana cost) and persist until the skill is removed or the run ends. Multiple orbit skills can be active simultaneously, each maintaining its own ring.

## 2. Player Fantasy

Your power radiates around you — and leaves its mark. Fire orbs scorch the ground at their orbit radius, ice shards leave frost trails, lightning arcs scar the arena floor. Enemies enter a space that remembers your elemental choices from the moment you arrive. You move through the battlefield and your orbiting weapons do the work — you focus on positioning while your build fights for you. Each orbit skill is a persistent expression of your elemental power, written on the world itself.

## 3. Detailed Rules

**Architecture:**
- `IOrbitCombatService` (interface) injected via VContainer in `GameplayLifetimeScope`
- `OrbitCombatService` manages active orbit rings, spawns/despawns orbit projectiles
- `OrbitRing` — runtime container: `SkillId`, `SkillDefinition`, `ProjectileCount`, `OrbitSpeed`, `OrbitRadius`, `CurrentAngle`, pooled projectile instances list
- `OrbitProjectile` — pooled MonoBehavior with a trigger collider, despawns on hit or when the ring is removed

**Orbit Activation:**
- When a skill is drafted (via DRAFT Event or Build State notification), `OrbitCombatService.SpawnOrbit(SkillId, PlayerTransform)` is called
- Spawn creates an `OrbitRing` and instantiates `ProjectileCount` pooled projectiles evenly spaced around the player at `OrbitRadius`
- Projectiles are positioned relative to the player in `LateUpdate()` — they inherit player movement

**Orbit Update (per frame):**
- Each `OrbitRing` advances `CurrentAngle += OrbitSpeed × Time.deltaTime`
- Projectile positions are computed as: `playerPos + (cos(angle), sin(angle)) × OrbitRadius`
- Orbit projectiles rotate in the XZ plane (Y-up), never leave the ground plane
- If the player moves, projectile positions update to maintain radius (they follow, not drag)

**Hit Detection Integration:**
- Each `OrbitProjectile` has a trigger collider. On `OnTriggerEnter` with an enemy, `HitEvent` is published
- Projectile is NOT consumed on hit — orbit projectiles persist and can hit multiple enemies
- A per-projectile hit cooldown (0.3s per enemy) prevents rapid re-hitting of the same target
- Hit cooldown is tracked per-projectile per-enemy via a `Dictionary<Collider, float>` (cleaned up on despawn)

**Orbit Removal:**
- When a skill is replaced or removed (Rune Draft re-roll, run end), `OrbitCombatService.RemoveOrbit(SkillId)` despawns all projectiles in that ring
- On zone transition: all orbits are cleared, re-spawned on zone entry from Build State
- On player death: orbits are destroyed

**Multiple Orbits:**
- Each orbit skill maintains its own independent ring
- Rings do not interact, phase through each other (no collision between orbit projectiles)
- Up to 5 simultaneous orbit skills (MVP limit; configurable)
- If the limit is exceeded, the oldest orbit is replaced (FIFO)

**Environmental Ground Traces (P1):**
- Orbit projectiles leave persistent ground traces matching their element — a faint scorch ring at the orbit radius where fire projectiles pass, frost lines for ice, scorched hairline fractures for lightning
- Traces use the decal projector system from VFX System (#15) — pooled, 30s lifetime, cleaned up on zone transition
- This makes the player's elemental composition visible on the arena floor — enemies enter a space marked by the player's previous runs

**Upgrades:**
- Upgrades affect existing orbit rings in real time
- `ProjectileCount` upgrade: if new count > current, spawn additional projectiles evenly spaced. If < current, remove excess (last-in-first-removed).
- `OrbitSpeed`, `OrbitRadius` upgrades: update `OrbitRing` parameters immediately
- `BaseDamage` upgrade: applied to subsequent `HitEvent` payloads (projectiles don't cache damage)

## 4. Formulas

```
projectileAngle(i) = baseAngle + (360° / projectileCount) × i
orbitPosition(i) = playerPosition + (cos(projectileAngle(i)), sin(projectileAngle(i))) × orbitRadius
hitCooldown = 0.3s (per enemy per projectile)
maxOrbitSkills = 5
```

Where:
- `baseAngle` — current `OrbitRing.CurrentAngle` (accumulated per frame)
- `projectileCount` — from `SkillDefinition.ProjectileCount`, modified by upgrades
- `orbitRadius` — from `SkillDefinition.OrbitRadius` (meters), modified by upgrades
- No other formulas. Orbit behavior is purely geometric.

## 5. Edge Cases

- **If player has no orbit skills active**: No orbit updates. `OrbitCombatService` has an empty ring list. Idle cost is zero.
- **If orbit radius exceeds arena bounds**: Projectiles wrap to the other side if the arena uses wrapping; otherwise they clip through bounds visual. Not a gameplay issue — enemies are inside the bounds.
- **If projectile count is 0** (misconfigured skill): Orbit ring is created with 0 projectiles. Log a warning. No crash. Skill visually has no projectiles until upgraded.
- **If orbit speed is 0**: Projectiles are stationary relative to the player. Still functional (minefield). Valid configuration.
- **If hit cooldown map for a projectile grows large** (many enemies): Per-projectile map is cleared on projectile despawn. Map is a standard Dictionary — no GC impact at reasonable sizes (max ~50 concurrent enemies in MVP).
- **If an orbit projectile hits the same enemy from multiple projectiles in the same ring**: Each projectile has its own hit cooldown timer per enemy. If two projectiles hit the same enemy simultaneously, both apply damage (unless both are on cooldown for that enemy). This is intentional — denser rings = more damage.
- **If the player levels up mid-rotation and an upgrade changes projectile count**: New projectiles are spawned at evenly distributed angles from the current `baseAngle`. No visual pop — they fade in over 0.2s.
- **If orbit skill is removed while projectiles are mid-hit-cooldown**: `RemoveOrbit` despawns all projectiles in the ring. Hit cooldown maps are discarded. No memory leak.
- **If Build State is empty on zone entry**: No orbit skills to spawn. Player starts zone with empty orbit list. Valid state (player chose no orbit skills).
- **If orbit upgrade reduces radius below 0.5m**: Radius is clamped to 0.5m minimum. Projectiles should not clip into the player model.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Skill Data System | #3 | Data | Reads orbit-specific fields from `SkillDefinition` |
| Damage & Health | #19 | Producer | Orbit hit → `HitEvent` → Damage & Health pipeline |
| Hit Detection | #8 | Producer | Orbit projectiles have trigger colliders that register with Hit Detection |
| Object Pooling | #4 | Dependency | `OrbitProjectile` prefabs are pooled |
| Build State | #29 | Data | Provides active orbit skill list on zone entry |
| Game State | #1 | Consumer | Clears orbits on `InRun → HeroCamp/Defeat/Victory` |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Per-enemy hit cooldown | 0.3s | 0.1–1.0s | Fast ticks, high DPS | Slow hits, orbit is visual only | OrbitCombatService |
| Max simultaneous orbit skills | 5 | 3–10 | Dense orbital field (visual noise risk) | Limited build expression | OrbitCombatService |
| Orbit radius minimum clamp | 0.5m | 0.25–1.0m | Stays visible outside player model | Clips into player | OrbitCombatService |
| New projectile fade-in | 0.2s | 0.0–0.5s | Smooth visual addition | Instant pop | OrbitCombatService |

## 8. Acceptance Criteria

1. **Orbit spawns on draft** — When an orbit skill is drafted, `OrbitRing` is created with `ProjectileCount` projectiles evenly spaced at `OrbitRadius`.
2. **Orbit rotates continuously** — Each frame, orbit projectiles rotate around the player at `OrbitSpeed` degrees/sec.
3. **Orbit follows player position** — Projectile positions update with player movement, maintaining `OrbitRadius`.
4. **Orbit hits enemies on contact** — When an orbit projectile's collider touches an enemy, `HitEvent` is published.
5. **Projectile is not consumed on hit** — After hitting an enemy, the projectile continues its orbit rotation.
6. **Per-enemy hit cooldown prevents rapid re-hits** — Same projectile cannot hit the same enemy more than once per 0.3s.
7. **Multiple orbit skills stack** — Each drafted orbit skill creates its own independent ring. All rings update simultaneously.
8. **Upgrade changes take effect immediately** — When an upgrade modifies `ProjectileCount`, `OrbitSpeed`, or `OrbitRadius`, the orbit ring updates in real time.
9. **Orbit cleared on zone transition** — When `GameStateChangedEvent` fires with a non-`InRun` state, all orbits are destroyed.
10. **Orbit re-spawned on zone entry** — When entering a new zone, orbits are rebuilt from Build State's active skill list.
11. **Max orbit limit enforced** — If the number of orbit skills exceeds the max, the oldest ring is removed.
12. **Zero projectile count logs warning** — Orbit ring with 0 projectiles logs a warning but does not crash.
13. **Orbit removal despawns projectiles** — When `RemoveOrbit(SkillId)` is called, all projectiles for that ring are returned to pool.
