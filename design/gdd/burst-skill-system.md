# Burst Skill System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (elemental status pipeline explicitly connected, P2 emergence section added, lore connection added)
> **Status**: Designed

> **System ID**: #21
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 19 (Foundation → Core → Feature → Presentation → Polish)
> **Depends on**: Skill Data System (#3), Damage & Health (#19), Hit Detection (#8), Object Pooling (#4), Time System (#6)
> **Depended by**: Build State (#29), HUD (#30), Skill Presentation (#34)

## 1. Overview

The Burst Skill System manages aimed, cooldown-gated skill execution. When the player activates a burst skill (LMB/RMB/gamepad button), the system reads the player's aim direction, resolves the target area from skill parameters (cast range, AoE radius, aim angle), spawns a projectile or hit effect, and resolves damage through Hit Detection. Cooldown is managed per-skill-instance via the Time System.

## 2. Player Fantasy

Your burst skills are your decisive actions — the fireball you aim into a swarm, the ice shard you snipe across the arena, the lightning arc you time to stun a charging boss. Each burst is a moment of intention: aim, fire, watch the element do its work. Cooldowns force meaningful choices between bursts. Burst skills are memories of destroyed civilizations — a fireball from the Fractured Pass carries the heat of a dying forge-city, a lightning arc from the Crystal Caverns buzzes with residual mineral charge.

## 3. Detailed Rules

**Architecture:**
- `IBurstSkillService` (interface) — injected via VContainer in `GameplayLifetimeScope`
- `BurstSkillService` — owns active burst skill instances, handles activation, cooldown tracking
- `BurstSkillInstance` — runtime container: `SkillId`, `SkillDefinition`, `RemainingCooldown` (driven by `ITimerService`)
- Player input reads burst skill activation from Input System actions, routes to `BurstSkillService.TryActivate(SkillId, AimData)`

**Activation Flow:**
1. Player presses burst input → `TryActivate(SkillId, AimData)` called
2. Check `RemainingCooldown > 0` → if true, activation rejected (silent, no cooldown UI flash)
3. Resolve target from `AimData` (mouse world position or gamepad aim direction + cast range)
4. If `AoeRadius > 0`: damage is resolved at target position (area). Otherwise: single-target (first enemy hit by projectile)
5. Spawn projectile (if `ProjectileKey` is set) or apply hit effect directly
6. Set `RemainingCooldown = SkillDefinition.CooldownSeconds`
7. Publish `SkillActivatedEvent(SkillId, ElementType, TargetPosition)` for Audio/VFX

**Elemental Status Application:**
- On hit, the burst's `ElementType` flows through the Damage pipeline → Status Effect System applies the matching status (Burn, Slow/Freeze, Stun).
- A fire burst hitting a non-burning enemy applies Burn. An ice burst at <50% HP applies Freeze.
- Clear cross-slot pattern: slot 1 fire burst applies Burn, slot 2 ice burst on the same burning enemy applies Slow (and Freeze if HP is low). The two elements accumulate independently — no special combo table needed in MVP.

**P2 Emergence (MVP):** Burst builds emerge from (a) picking two elements with complementary statuses (Burn pressure + Freeze burst), (b) sequencing casts for effect (fire to push HP below 50% → ice to freeze → next ice hit does 2x), and (c) upgrade choices that shift the skill's role (wider AoE for wave clear vs. more damage for boss dps). No explicit combo table exists — discovery comes from simple rules interacting.

**Aim Resolution:**
- Mouse: `AimData.TargetPosition = Camera.ScreenToWorldPoint(mousePosition)`, clamped to `CastRange` from player
- Gamepad: Direction vector × `CastRange`, added to player position
- If `AimAngle < 360`: cone-shaped AoE centered on aim direction
- If `AimAngle == 360`: omni-directional (all enemies in `AoeRadius`)
- If `AoeRadius == 0` and `AimAngle == 0`: single-target projectile (first enemy hit)

**Projectile Behavior:**
- Burst projectiles travel from player toward target position over `flightTime = distance × 0.1s` (configurable)
- On reaching target: if AoE, hit all enemies in `AoeRadius`. If single-target, hit first enemy in path
- Projectile has trigger collider for intermediate hits (if it hits an enemy before reaching max range, resolve hit early)
- Projectile is despawned on hit or at max range
- Projectiles use `ProjectileKey` → resolved via `ProjectileRegistry` in Skill Presentation

**Cooldown:**
- Cooldown timer runs in real-time (affected by Time System's `timeScale`)
- `RemainingCooldown` decremented each frame via `ITimerService`
- Cooldown does not tick down while game is paused (Time System handles this)
- Multiple burst skill instances each have independent cooldowns

**Multiple Burst Skills:**
- Player can have up to 2 burst skills active simultaneously (MVP limit)
- Each bound to a separate input (LMB = burst slot 1, RMB = burst slot 2)
- More burst slots deferred to Alpha (keyboard 1-4)
- Each slot has its own cooldown, independent activation

**Upgrades:**
- `BaseDamage` upgrade: applied to next activation's damage calculation
- `CooldownSeconds` upgrade: reduced if new value < current (immediate cooldown reduction proportional to upgrade delta)
- `AoeRadius` upgrade: increases on next activation
- `ProjectileCount` upgrade: spawns additional projectiles in a spread pattern (`AimAngle / projectileCount` apart)

**Input Integration:**
- `BurstSkillService` listens to `OnBurstSkill1` and `OnBurstSkill2` input actions
- On press: reads current `AimData` from Input System's aim action
- On release: nothing (press-to-fire, no charge mechanic)

## 4. Formulas

```
projectileFlightTime(distance) = distance × 0.1s
cooldownMultiplier(upgrade) = 1.0 - (upgrade.cooldownReduction / 100f)
projectileSpreadAngle(i, count) = (aimAngle / count) × i - (aimAngle / 2)
```

Where:
- `distance` — vector magnitude from player to target position
- `upgrade.cooldownReduction` — percentage reduction from upgrade tier
- `aimAngle` — from `SkillDefinition.AimAngle`
- `count` — from `SkillDefinition.ProjectileCount`, modified by upgrades

## 5. Edge Cases

- **If burst skill is activated while on cooldown**: Silent reject. No event published. No UI feedback (cooldown UI already shows fill).
- **If burst skill fires and the player dies before the projectile reaches target**: Projectile remains in flight and resolves on hit. `DamageDealtEvent` still processes. Projectile despawns normally.
- **If target position is out of cast range**: Clamped to `CastRange` from player. Visual target indicator shows max range.
- **If AoE radius covers 0 enemies**: Hit event resolves with 0 targets. No `DamageDealtEvent` published. Projectile despawns normally at position.
- **If AimAngle is 0 and AoeRadius is 0**: Single-target projectile that hits the first enemy in its path. If no enemy hit by max range, projectile despawns with no effect.
- **If BurstSkill1 input is pressed while slot 1 has no skill**: Silent no-op. No crash. (This is a pre-game validation issue — player cannot have empty slots in normal flow.)
- **If cooldown is reduced to 0 by upgrade**: Cooldown is set to 0. Next activation has no wait. Valid — fully upgraded burst becomes spammable.
- **If projectile is despawned by zone transition while in flight**: All projectiles are cleaned up on `GameStateChangedEvent` (non-InRun). Pool despawns. No orphaned projectiles.
- **If player activates burst and immediately activates another burst in the same frame**: Both process sequentially. Each has independent cooldown. No interference.
- **If burst projectile hits multiple enemies in a single frame** (AoE burst): All enemies in radius are hit. `HitEvent` is published per enemy. Damage & Health processes each independently.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Skill Data System | #3 | Data | Reads burst-specific fields from `SkillDefinition` |
| Damage & Health | #19 | Producer | Burst hit → `HitEvent` → Damage & Health pipeline |
| Hit Detection | #8 | Producer | Burst projectiles register trigger colliders |
| Object Pooling | #4 | Dependency | Burst projectiles are pooled via `ProjectileKey` |
| Time System | #6 | Dependency | Cooldown timers via `ITimerService` |
| Input System | #5 | Consumer | Listens to `OnBurstSkill1`, `OnBurstSkill2`, aim actions |
| Skill Presentation | #34 | Consumer | Projectile visual/audio on activation |
| Build State | #29 | Data | Provides assigned burst skill IDs per slot |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Projectile flight time multiplier | 0.1s/m | 0.05–0.3 | Slow travel, dodgeable | Hitscan | BurstSkillService |
| Max burst skill slots | 2 | 1–4 | High burst variety | Simple, focused loadout | BurstSkillService |
| Cooldown floor (min possible) | 0.0s | 0.0–1.0 | Zero cd on max upgrade | Always some wait | BurstSkillService |

## 8. Acceptance Criteria

1. **Burst skill fires on input** — When burst input is pressed and cooldown is ready, burst activates at aim position.
2. **Cooldown prevents re-fire** — Activating while on cooldown is silently rejected.
3. **Projectile spawns and travels** — When activated, a pooled projectile spawns at player position and travels toward target.
4. **AoE hits all enemies in radius** — When burst has `AoeRadius > 0`, all enemies in the radius at target position take damage.
5. **Single-target hits first enemy in path** — When burst has no AoE, the first enemy hit by the projectile takes damage.
6. **Cooldown counts down** — After activation, cooldown timer decrements to 0 before the skill can fire again.
7. **Independent slot cooldowns** — Each burst skill slot has its own cooldown; firing slot 1 does not affect slot 2's cooldown.
8. **Out-of-range target clamped** — If aim position exceeds `CastRange`, target is clamped to max cast range.
9. **Projectile despawns on hit** — After resolving a hit, the projectile returns to pool.
10. **Projectile despawns at max range** — If projectile reaches max range without hitting, it returns to pool.
11. **Omni-directional burst hits all around** — Burst with `AimAngle = 360` hits all enemies in `AoeRadius` around the player.
12. **Cone burst hits only in cone** — Burst with `AimAngle < 360` only hits enemies within the cone from aim direction.
13. **Upgrades apply to next activation** — Upgrading damage/cooldown/radius affects the next burst activation, not a currently-in-flight projectile.
