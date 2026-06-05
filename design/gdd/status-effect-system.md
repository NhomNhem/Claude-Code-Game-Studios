# Status Effect System

> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED — 2026-05-29
> **Status**: Designed

> **System ID**: #18
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 16 (Foundation → Core → Feature → Presentation → Polish)
> **Depends on**: Skill Data System (#3), Time System (#6)
> **Depended by**: Damage & Health (#19), Enemy AI (#24), Boss (#26)

## 1. Overview

The Status Effect System manages elemental status conditions applied to enemies (and potentially the player) when damage of a matching element lands. Fire burns, Ice slows/freezes, Lightning stuns. Effects are duration-based with tick timers, managed by the Time System. The system is an Event Bus consumer of `DamageDealtEvent` and resolves the status from the damage's element type.

## 2. Player Fantasy

Elemental hits mean more than just damage numbers. When you hit an enemy with fire, it burns. Ice cracks through a frozen enemy. Lightning stuns in place. The element you choose changes how the fight feels — not just how much damage you do. Status effects are the tactile expression of elemental identity.

## 3. Detailed Rules

**Architecture:**
- `IStatusEffectService` (interface) injected via VContainer in `GameplayLifetimeScope`
- `StatusEffectService` subscribes to `DamageDealtEvent` in `Start()`, manages active status instances
- `StatusInstance` tracks: target entity, status type, remaining duration, tick timer, tick count

**Element → Status Mapping:**

| Element | Status | Effect | Tick Interval | Duration | Stacking |
|---------|--------|--------|---------------|----------|----------|
| Fire | Burn | DOT: deals 5% of base damage per tick | 1.0s | 3.0s | Refresh duration |
| Ice | Slow | Move speed -40%, attack rate -20% | — (continuous) | 2.0s | Refresh duration |
| Ice (stacked at 50% hp) | Freeze | Rooted, no actions, 2x damage from next hit | — | 1.5s | Cannot re-freeze |
| Lightning | Stun | Rooted, no actions | — | 0.5s | Refresh duration |

**Status Application:**
- On `DamageDealtEvent`, read `DamageSource.ElementType`:
  - `Fire` → apply Burn to target
  - `Ice` → apply Slow. If target HP < 50%, upgrade to Freeze
  - `Lightning` → apply Stun
- If status is already active: refresh duration (no stacking for MVP)
- Freeze has a cooldown (cannot freeze same target for 5s after freeze ends)
- Status application happens regardless of damage being lethal (enemy about to die still gets the status frame)

**Tick Countdown:**
- Burn ticks on a per-enemy timer (1.0s interval). Tick deals DOT damage by publishing `DamageDealtEvent` with zero position and `DamageType = StatusEffect`.
- Slowed/frozen/stunned enemies are tracked via a flag on the enemy's movement/action controller
- When duration expires: status removed, reset any modified stats

**Status Removal:**
- On duration expiry (automatic)
- On enemy death (all statuses cleared)
- On zone transition (all statuses cleared — enemies despawn)
- Manual removal via `ClearStatus(EntityId, StatusType)`

**Player Status Effects (MVP Scope):**
- Players receive NO status effects in MVP. Enemy attacks deal raw damage only.
- Player status effects are deferred to Alpha (enemy elemental attacks, status-immune passives)

**Post-MVP Narrative Status Behavior (Deferred):**
- Burning enemies panic and spread fire to nearby allies (environmental storytelling)
- Frozen enemies shatter into slowing ice shards on death
- Stunned enemies recover dazed (brief confused state)
- Not in scope for MVP — no design work required now

## 4. Formulas

```
BurnTickDamage = DamageDealtEvent.Amount × 0.05
FreezeBonusDamage = DamageTaken × 2.0
StatusDuration(element) = element.BaseDuration × DurationMultiplier(runTime)
FreezeCooldown = 5.0s (fixed)
```

Where:
- `DamageDealtEvent.Amount` — the raw damage dealt in the triggering hit
- `element.BaseDuration` — per-element base duration (3.0s fire, 2.0s ice, 1.5s freeze, 0.5s lightning)
- `DurationMultiplier(runTime)` — linear 1.0→1.3 over run length (statuses last longer in late waves)
- No other formulas. Status effects are duration-driven, with no escalating DOT damage for MVP.

## 5. Edge Cases

- **If DamageDealtEvent has ElementType.None** (non-elemental damage): No status applied. Silent no-op.
- **If same enemy is hit by Fire 10 times in 1 second**: Burn is refreshed each time. Duration resets to 3.0s. No stacking, no extra ticks.
- **If enemy dies from Burn DOT**: The status tick publishes DamageDealtEvent, which triggers normal death logic. Burn does not need to check for overkill.
- **If status is applied to an immune enemy** (boss with status immunity): Status is ignored. Log warning. No effect.
- **If Freeze cooldown is active and enemy drops below 50% HP**: Slow is applied but not upgraded to Freeze. Freeze is attempted but silently rejected.
- **If status duration expires while Burn tick is in flight**: Tick resolves first (damage dealt), then duration check removes status. Order guaranteed by tick timer vs duration timer running on the same clock.
- **If an entity already has Freeze and Stun is applied** (shouldn't happen with MVP single-element hits): Freeze takes priority. Stun is discarded.
- **If enemy is killed while frozen**: Freeze is removed on death. No special freeze death interaction.
- **If zone transitions while status is active**: All active statuses are cleared. StatusInstance list is emptied. No leak.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Skill Data System | #3 | Consumer | Reads `ElementType` from damage source skill |
| Time System | #6 | Dependency | Tick timers, duration timers via ITimerService |
| Event Bus | #2 | Consumer | Subscribes to `DamageDealtEvent` |
| Damage & Health | #19 | Producer | Recipient of Burn DOT `DamageDealtEvent` publishes |
| Enemy AI | #24 | Consumer | Reads `HasStatus(EntityId, StatusType.Slow/Stun/Freeze)` |
| Boss Encounter | #26 | Consumer | May declare boss immune to specific statuses |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Burn DOT % of base damage | 5% | 2–15% | Significant DOT pressure | Barely noticeable | StatusEffectService |
| Burn tick interval | 1.0s | 0.5–2.0s | Fast ticks, more DOT resolution | Slow ticks, smoother damage | StatusEffectService |
| Burn duration | 3.0s | 1.5–6.0s | Long burn, high uptime | Short burn, often wears off | StatusEffectService |
| Slow move speed penalty | 40% | 20–60% | Nearly rooted | Gentle slowdown | StatusEffectService |
| Slow duration | 2.0s | 1.0–4.0s | Long slowdown | Barely matters | StatusEffectService |
| Stun duration | 0.5s | 0.25–1.5s | Significant CC window | Micro-stun | StatusEffectService |
| Freeze duration | 1.5s | 0.75–3.0s | Long damage window | Short root | StatusEffectService |
| Freeze bonus damage | 2.0x | 1.5–3.0x | Big burst reward | Modest bonus | StatusEffectService |
| Freeze cooldown | 5.0s | 3.0–10.0s | Frequent freeze attempts | Rare freeze | StatusEffectService |
| Duration multiplier max | 1.3x | 1.0–2.0x | Statuses dominate late runs | Consistent duration | StatusEffectService |
| Ice freeze threshold | 50% HP | 25–75% | Freeze triggers early | Freeze triggers near death | StatusEffectService |

## 8. Acceptance Criteria

1. **Fire hit applies Burn** — When `DamageDealtEvent` with `ElementType.Fire` fires, a Burn status is applied to the target.
2. **Burn ticks deal DOT** — Every tick interval, Burn publishes a `DamageDealtEvent` with 5% of original damage and `DamageType = StatusEffect`.
3. **Burn duration refresh** — If Burn is already active when a new Fire hit lands, duration resets to 3.0s.
4. **Burn expires after duration** — After 3.0s without refresh, Burn is removed.
5. **Ice hit applies Slow** — When `DamageDealtEvent` with `ElementType.Ice` fires, Slow status is applied (move speed -40%, attack rate -20%).
6. **Ice at <50% HP applies Freeze** — If target HP < 50%, Ice hit applies Freeze (rooted, 2x next hit damage) instead of Slow.
7. **Freeze cooldown** — Freeze cannot be reapplied to the same target within 5s of its expiry.
8. **Lightning hit applies Stun** — When `DamageDealtEvent` with `ElementType.Lightning` fires, Stun status is applied (rooted, 0.5s).
9. **Status duration refresh on re-application** — Re-applying the same status refreshes duration (no stacking).
10. **Status cleared on death** — When an enemy dies, all active statuses are removed.
11. **Status cleared on zone transition** — When zone transitions, all active status instances are cleared.
12. **Non-elemental damage does nothing** — `DamageDealtEvent` with `ElementType.None` applies no status.
13. **Boss immunity works** — If a boss declares immunity to a status type, that status is silently rejected.
14. **Single freeze per cooldown period** — Attempting to freeze a target within freeze cooldown results in Slow application only.
