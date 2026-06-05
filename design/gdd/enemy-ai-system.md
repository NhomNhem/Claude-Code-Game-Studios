# Enemy AI System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (elemental affinity, rift origin, visual tells added for P1/P2)
> **Status**: Designed

> **System ID**: #24
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 22
> **Depends on**: Game State (#1), Hit Detection (#8), Object Pooling (#4)
> **Depended by**: Boss Encounter (#26), Wave Spawning (#25), Currency (#11), Level-Up (#22)

## 1. Overview

The Enemy AI System defines the behavior of all non-boss enemies. Each enemy type has a state machine (Spawn → Idle → Chase/Patrol → Attack → Death), movement pattern, attack pattern, and target acquisition rules. Enemies are pooled and activated by Wave Spawning. The system is data-driven via EnemyDefinition ScriptableObjects.

## 2. Player Fantasy

Every enemy type fights differently and carries the memory of its rift origin. Melee enemies from the Fractured Pass charge with amber-tinted fury, ice crystal enemies from the Caverns shatter-resistant under fire but melt under pressure. You read not just movement patterns but elemental tells — a fire-glow charger needs ice to break, a lightning turret is tough but stuns briefly on hit. Each movement and attack is readable, and your build choices matter differently against each type.

## 3. Detailed Rules

**Architecture:**
- `IEnemyAIService` (interface) injected via VContainer in `TinyRiftScope`
- `EnemyAIService` — updates active enemies each frame, drives state machines
- `EnemyAIState` — per-enemy enum-based state (Spawn → Idle → Chase → Attack → Flee → Death)
- `EnemyDefinition` — ScriptableObject: HP, movespeed, damage, XP value, behavior type, attack pattern, element, rift origin, elemental weakness table, elemental resistance table

**Elemental Affinity:**
- Each enemy has an assigned element (matching its rift origin) and optional weakness/resistance table
- Fire-element enemy: resists fire (0.5x), vulnerable to ice (1.5x)
- Ice-element enemy: resists ice (0.5x), vulnerable to fire (1.5x)
- Lightning-element enemy: resists lightning (0.5x), no elemental weakness in MVP (design gap for future element)
- Status effects apply normally — burning an ice enemy still deals Burn DOT
- Elemental affinity affects visual tint: fire enemies glow orange, ice enemies glow blue-white, lightning enemies glow purple
- The affinity table is authored per `EnemyDefinition`, not globally — designers can override per enemy type

**Rift Origin:**
- Each `EnemyDefinition` declares which zone it spawns in via `RiftOrigin` field (zone_fractured_pass, zone_crystal_caverns, zone_ash_circle)
- Spawn VFX includes a color flash matching the rift origin color (Fractured Pass = amber, Crystal Caverns = cyan, Ash Circle = crimson)
- Players learn to identify enemy origin by visual tells, connecting combat to world lore

**States:**
| State | Entry | Behavior | Exit |
|-------|-------|----------|------|
| Spawn | On pooled activation | Play spawn VFX, 0.5s invulnerable, no movement | → Idle after animation |
| Idle | After spawn / patrol reset | Stand still, face nearest target direction | → Chase if target in aggro range |
| Chase | Target in aggro range | Move toward target at movespeed | → Attack if target in attack range |
| Attack | Target in attack range | Execute attack pattern, animation-driven | → Chase after attack cooldown |
| Flee | HP < flee threshold (if configured) | Move away from target at 1.5x movespeed | → Chase after 3s or out of flee range |
| Death | HP <= 0 | Play death VFX, publish EntityDiedEvent, despawn to pool | — |

**Behavior Types (MVP):**
| Behavior | Movement | Attack | Notes |
|----------|----------|--------|-------|
| MeleeCharger | Straight toward player | Melee swing, 1.0s cooldown | Basic enemy, closes distance fast |
| RangedCaster | Strafe at 5-8m distance | Projectile lob, 2.0s cooldown | Keeps distance, kites player |
| SuicideBomber | Fast charge toward player | Explodes on contact, kills self | Area denial, high threat |
| Orbiter | Circle at 4m radius | Melee every 1.5s | Packs of these flank the player |
| Turret | Stationary | Projectile burst every 3s | Positioned at fixed locations by wave config |

**Target Acquisition:**
- Primary target: nearest player (always)
- Aggro range: 12m (configurable per enemy type)
- Chase range: once aggroed, stays aggroed until 20m away or player dies
- No threat table or aggro swap (MVP — player is always the target)
- No allied targeting (no friendly fire, no self-target)

**Attack Resolution:**
- Melee: on `OnTriggerEnter` with player during attack state, publish `HitEvent` from enemy to player
- Ranged: spawn pooled projectile via Skill Presentation / ProjectileRegistry, projectile publishes `HitEvent` on contact
- Suicide: on contact with player, deal damage and publish `EntityDiedEvent` (self)
- Attack cooldown tracked per enemy via `ITimerService`

**Wave Integration:**
- Enemies are activated by Wave Spawning from pool
- `GameStateChangedEvent(InRun → Hub/HeroCamp)`: deactivate all enemies, return to pool
- `GameStateChangedEvent(BossActive)`: remaining non-boss enemies deactivate (clear arena for boss)

## 4. Formulas

```
aggroRange(base) = base × aggroRangeMultiplier(runTime)
attackCooldown(base) = base × cooldownMultiplier(runTime)
enemyDamageOutput = baseDamage × damageMultiplier(runTime)
```

Where:
- `aggroRangeMultiplier(runTime)` — linear 1.0→1.3 over run length
- `cooldownMultiplier(runTime)` — linear 1.0→0.8 over run length (enemies attack faster late-run)
- `damageMultiplier(runTime)` — linear 1.0→1.5 over run length (enemies hit harder late-run)

## 5. Edge Cases

- **If target is out of chase range**: Enemy returns to Idle at current position. Never teleports back to spawn.
- **If enemy reaches attack range but is on cooldown**: Stay in Chase state, circle near player until cooldown expires.
- **If enemy has no path to player** (obstacle): Use simple direction-based movement (no pathfinding in MVP). Enemy walks toward player direction, may clip obstacles.
- **If all players are dead**: Transition to Idle. No attacks. Enemies stand still until run ends.
- **If enemy is pooled while in mid-attack**: Force-transition to Death state → despawn. No orphaned attack coroutines.
- **If suicide bomber kills itself but the explosion hits no one**: `EntityDiedEvent` still publishes (self-death). No `HitEvent` for explosion.
- **If enemy spawns with player in aggro range**: Immediate Chase state entry. No Idle dwell.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Game State | #1 | Consumer | Listens for zone state changes for cleanup |
| Hit Detection | #8 | Producer | Attacks publish `HitEvent` |
| Object Pooling | #4 | Dependency | Enemies are pooled via pool key |
| Wave Spawning | #25 | Trigger | Activates/deactivates enemy pool members |
| Time System | #6 | Dependency | Attack cooldowns, flee timer |
| Skill Presentation | #34 | Consumer | Ranged projectiles via ProjectileRegistry |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Base aggro range | 12m | 8–20m | Enemies aggro early | Surprise attacks up close | EnemyDefinition |
| Chase leash range | 20m | 15–30m | Enemies chase far | Enemies give up easily | EnemyDefinition |
| Spawn invuln duration | 0.5s | 0.0–1.0s | Safe spawns | Immediate vulnerability | EnemyDefinition |
| Aggro range scaling | 1.3x | 1.0–1.5x | Late-run enemies aggro from far | Consistent range throughout | WaveConfig |
| Attack cooldown scaling | 0.8x | 0.5–1.0x | Late-run enemies attack very fast | Consistent pace | WaveConfig |
| Damage scaling | 1.5x | 1.0–2.0x | Late-run hits hurt a lot | Consistent damage | WaveConfig |

## 8. Acceptance Criteria

1. **Enemy spawns in Idle** — On pool activation, enemy enters Spawn then Idle state.
2. **Enemy aggroes within range** — When player enters aggro range, enemy transitions to Chase.
3. **Enemy attacks in attack range** — When player enters attack range and cooldown is ready, enemy executes attack pattern.
4. **Melee hit publishes HitEvent** — On melee contact during attack state, `HitEvent` is published.
5. **Ranged enemy fires projectile** — Ranged enemy spawns pooled projectile on attack.
6. **Suicide bomber explodes on contact** — On contact with player, enemy deals damage and kills itself.
7. **Enemy dies at 0 HP** — When HP reaches 0, `EntityDiedEvent` is published and enemy returns to pool.
8. **Enemy returns to pool on zone transition** — When `GameStateChangedEvent` fires with non-run state, all enemies deactivate.
9. **Attack cooldown is respected** — Enemy does not attack more frequently than its cooldown allows.
10. **Flee behavior moves away** — If enemy has flee threshold and HP drops below it, enemy moves away from player.
11. **Out-of-range enemy stops chasing** — When player exceeds chase range, enemy returns to Idle at current position.
12. **Orbiter circles at configured radius** — Orbiter-type enemy maintains distance while moving around player.
