# Damage & Health System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (lore-derived weakness tables, player-facing weakness signal added)
> **Status**: Designed

> **System ID**: #19
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 17 (Foundation → Core → Feature → Presentation → Polish)
> **Depends on**: Skill Data System (#3), Event Bus (#2), Status Effect System (#18), Time System (#6)
> **Depended by**: Orbit Combat (#20), Burst Skill (#21), Enemy AI (#24), Boss (#26), Screen Shake (#27), HUD (#30), Level-Up (#22), Currency (#11)

## 1. Overview

The Damage & Health System is the authoritative resolver of all hit outcomes. It subscribes to `HitEvent` from Hit Detection, calculates final damage (mitigation, vulnerability, status modifiers), applies it to the target's health pool, publishes `DamageDealtEvent`, and detects death (publishing `EntityDiedEvent`). It also manages player invulnerability frames and per-entity damage resistance.

## 2. Player Fantasy

Every hit lands with consequence. Damage numbers reflect your build choices — a fire-weak enemy melts under your DOT, a frozen boss takes double damage from your next burst. The player's health bar is precious and protected by brief i-frames after each hit. You feel every point of damage you deal and receive.

## 3. Detailed Rules

**Architecture:**
- `IDamageHealthService` (interface) injected via VContainer in `GameplayLifetimeScope`
- `DamageHealthService` subscribes to `HitEvent` in `Start()`, tracks entity health via `HealthComponent`
- `HealthComponent` — MonoBehavior or component attached to entities: `MaxHp`, `CurrentHp`, `DamageResistance`, `IsInvulnerable`, `IFrameTimer`

**Health Component:**
```
HealthComponent :
  string EntityId         — stable entity identifier
  float MaxHp             — from entity definition
  float CurrentHp         — mutable runtime
  float BaseResistance    — base damage reduction (0.0 = none, 0.5 = 50%)
  float StatusResistance  — additional resistance from status effects
  bool IsInvulnerable     — true during i-frames
  float IFrameTimer       — remaining i-frame time
  Action<float> OnHpChanged — callback for HUD updates
```

**Damage Pipeline (per `HitEvent` received):**
1. Validate source and target are alive and in-game
2. Check target `IsInvulnerable` — if true, skip damage entirely
3. Resolve base damage from hit data (weapon/skill base damage)
4. Apply damage resistance: `afterResistance = baseDamage × (1 - totalResistance)`
5. Apply status effect bonuses: `FreezeBonus = 2.0× if target is Frozen`
6. Apply elemental weakness/resistance if defined on entity
7. Apply `DamageDealtEvent.TargetHp = CurrentHp - finalDamage`, clamp to 0
8. Set `CurrentHp = TargetHp`
9. Publish `DamageDealtEvent` with final values
10. If `CurrentHp <= 0`: set `CurrentHp = 0`, publish `EntityDiedEvent`
11. Notify `OnHpChanged` callback

**Damage Dealt Event Schema:**
```
readonly record struct DamageDealtEvent :
  EntityId Source         — attacker
  EntityId Target         — victim
  float Amount            — final damage applied
  float TargetHp          — Hp after damage (for HUD, not for further processing)
  ElementType ElementType — from source skill
  DamageType DamageType   — Normal, StatusEffect, True
  Vector3 HitPosition     — world position of impact
```

**Entity Died Event Schema:**
```
readonly record struct EntityDiedEvent :
  EntityId Target         — the entity that died
  EntityId Killer         — the entity that killed it (may be null for environment kills)
  ElementType KillingElement — element of the killing blow
  Vector3 DeathPosition   — world position of death
```

**Player Health:**
- Player `HealthComponent` is created on player spawn, destroyed on death/respawn
- Player base HP: 100 (configurable)
- Player takes damage from enemy attacks only (no friendly fire)
- On player death: publish `GameStateChangedEvent(InRun, Defeat)` via GState, which triggers Run Manager

**Invulnerability Frames (Player):**
- After taking damage, player is invulnerable for 0.5s (configurable)
- During i-frames: `IsInvulnerable = true`, damage is skipped
- I-frame timer is decremented by `ITimerService` each tick
- Visual feedback: brief alpha flicker on player sprite (owned by VFX/Skill Presentation)
- I-frames do not prevent status effects (burn DOT pierces i-frames)

**Damage Resistance:**
- `DamageResistance` is a scalar 0.0–0.9 (capped at 90%)
- Elemental weakness: `WeaknessMultiplier = 1.5×` for element weakness, `0.5×` for resistance
- Resistance is a property of entity definitions (enemy types, boss phases)
- Player has no base resistance in MVP (deferred to items/passives in Alpha)
- Freeze bonus is applied after resistance: `FreezeBonus = 2.0×`

**Enemy Health:**
- Enemy HP is defined per enemy type in Enemy AI or Zone Definition
- No per-enemy damage resistance in MVP (all enemies have 0.0 base resistance)
- Bosses have phased HP (each phase = portion of total HP)
- Elemental weakness/resistance configurable per enemy type (MVP: at least one weakness per enemy)
- **Lore-derived weakness authorship**: Crystal enemies resist fire (forged in volcanic rites), take extra lightning (conductive mineral structure). Ash ember enemies resist ice (warm core), take extra water/ice (quenched). Weakness tables are world-building tools, not random assignments — the player learns the world's history through combat.
- **Player-facing weakness signal**: When the player deals damage with an element the target is weak to, a brief element-colored tint pulse (0.3s) plays on the target. When resisted, a small gray "resist" text floats up. These signals ensure the player discovers weaknesses without opening a menu — keeping P3 snappiness.

**Healing (MVP Scope):**
- No player healing in MVP. HP persists between waves (no regen).
- Health pickups are deferred to Alpha (regen, health orbs)
- Boss phase transitions may restore a portion of boss HP (phase gate design)

## 4. Formulas

```
finalDamage = baseDamage × (1 - totalResistance) × freezeMultiplier × elementMultiplier
totalResistance = min(BaseResistance + StatusResistance, 0.9)
freezeMultiplier = target.HasStatus(Freeze) ? 2.0 : 1.0
elementMultiplier = weaknessTable[element] ?? 1.0
playerIFrameDuration = 0.5s
```

Where:
- `baseDamage` — from `HitEvent` (originating from skill's `BaseDamage`)
- `BaseResistance` — entity-defined scalar (0.0 for MVP enemies, 0.0 for player)
- `StatusResistance` — additive modifier from status effects (e.g., armor break in future)
- `weaknessTable` — per-entity `Dictionary<ElementType, float>` mapping element → damage multiplier
- No damage variance (no +/-% random range) in MVP — hits are deterministic

## 5. Edge Cases

- **If HitEvent fires with destroyed or despawned target**: Validate target's `HealthComponent` exists. If null, skip silently.
- **If damage exceeds remaining HP** (overkill): `CurrentHp` clamps to 0. No negative HP. Overkill damage is not tracked or propagated.
- **If HitEvent fires during i-frames**: Damage is skipped. `DamageDealtEvent` is NOT published. Silent no-op.
- **If player takes damage from multiple sources in the same frame**: First hit lands (i-frame begins). Second hit skips because i-frames are active. This is intentional — single-frame multi-hit protection.
- **If two HitEvents target the same enemy in the same frame**: Both process sequentially. No guarantee of ordering. If both are lethal, the first kills and the second receives a destroyed target (handled by edge case #1).
- **If a `DamageDealtEvent` subscriber throws**: Event Bus handles this per-subscriber. `DamageHealthService` continues to process subsequent subscribers normally.
- **If `EntityDiedEvent` recipient adds XP/currency before death animation plays**: This is correct — gameplay resolution is atomic, animation is cosmetic. Systems that need sync wait for explicit animation events, not death events.
- **If enemy is killed by a Burn DOT tick**: Burn tick publishes `DamageDealtEvent` → `HealthComponent.CurrentHp <= 0` → `EntityDiedEvent` with killer = the original damage source (tracked on the StatusInstance). The DOT does not need its own kill logic.
- **If player health reaches 0 during a frame with multiple simultaneous hits**: First lethal hit triggers death. `GameStateChangedEvent(InRun, Defeat)` fires. Subsequent hits are dropped because `HealthComponent` is being destroyed.
- **If a hit deals 0 or negative damage**: `finalDamage` is clamped to `max(0, calculatedDamage)`. Negative damage would heal — not allowed in MVP. Healing-in-damage is deferred.
- **If entity has no weakness entry for an element**: `weaknessTable[element]` returns null → `elementMultiplier` defaults to 1.0.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Event Bus | #2 | Consumer + Producer | Subscribes `HitEvent`, publishes `DamageDealtEvent`, `EntityDiedEvent` |
| Skill Data System | #3 | Data | Reads `BaseDamage`, `ElementType` from source skill definition |
| Status Effect System | #18 | Consumer | Queries `HasStatus()` for freeze bonus |
| Time System | #6 | Dependency | I-frame timer via `ITimerService` |
| Hit Detection | #8 | Producer | Publishes `HitEvent` that Damage & Health consumes |
| Game State | #1 | Producer | Publishes `GameStateChangedEvent(Defeat)` on player death |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Player base HP | 100 | 50–300 | Very tanky | Glass cannon | DamageHealthService |
| Player i-frame duration | 0.5s | 0.25–1.5s | Generous invulnerability | Tight timing, punishment | DamageHealthService |
| Max damage resistance cap | 0.9 | 0.75–1.0 | Near-invulnerable with high resist | Hard cap prevents immunity | DamageHealthService |
| Freeze damage bonus | 2.0x | 1.5–3.0x | Big burst reward | Modest bonus | DamageHealthService |
| Element weakness multiplier | 1.5x | 1.25–2.0x | Dramatic weakness pressure | Gentle incentive | EntityDefinition |
| Element resistance multiplier | 0.5x | 0.25–0.75x | Near-immune | Slight resistance | EntityDefinition |

## 8. Acceptance Criteria

1. **HitEvent applies damage** — When `HitEvent` is published, final damage is calculated and applied to target `HealthComponent.CurrentHp`.
2. **DamageDealtEvent published after damage** — After applying damage, `DamageDealtEvent` is published with correct `Amount`, `TargetHp`, `ElementType`.
3. **EntityDiedEvent published on death** — When `CurrentHp` reaches 0, `EntityDiedEvent` is published with correct `Target` and `Killer`.
4. **Player i-frames prevent damage** — After taking damage, player is invulnerable for 0.5s. Subsequent hits during this window are skipped.
5. **Freeze bonus damage** — If target has Freeze status, damage is multiplied by 2.0×.
6. **Elemental weakness multiplies damage** — If target has a weakness entry for the hit element, damage is multiplied by 1.5×.
7. **Overkill clamped to zero** — If damage exceeds remaining HP, `CurrentHp` is set to 0 (not negative).
8. **Zero resistance entities take full damage** — Entity with `BaseResistance = 0` takes full calculated damage (minus any status modifiers).
9. **Destroyed target is handled gracefully** — `HitEvent` for a destroyed/despawned target is silently skipped.
10. **Player death triggers defeat** — When player `CurrentHp` reaches 0, `GameStateChangedEvent(InRun, Defeat)` is published.
11. **Burn DOT from Status Effect correctly attributes killer** — When Burn DOT kills, `EntityDiedEvent.Killer` is the original attacker (tracked by StatusInstance), not the status system.
12. **No damage during i-frames does not publish DamageDealtEvent** — Skipped damage from i-frames does not produce a `DamageDealtEvent`.
13. **Element resistance reduces damage** — Entity with element resistance (0.5×) takes half damage from that element.
