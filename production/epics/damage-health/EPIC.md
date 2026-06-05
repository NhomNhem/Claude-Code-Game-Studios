# Epic: Damage & Health

> **Layer**: Gameplay
> **System**: Damage & Health
> **GDD**: `design/gdd/damage-health.md`
> **Architecture Module**: Damage & Health
> **Status**: Stories Not Ready
> **Stories**: 1 (001 — Draft)

## Overview

Wraps the template's existing `IDamageable`, `MonsterHealth`, and `CharacterAttackComponent` with a structured Damage & Health system. Provides `HealthComponent` (maxHP, currentHP, damage, healing, death), a `DamageApplicationService` that consumes `HitEvent` from the Event Bus, and publishes `DamageApplied` / `EntityDied` events for downstream systems (HUD, VFX, Wave Spawning, Score).

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |
| ADR-002: Event Bus Contract | Consumes HitEvent, publishes DamageApplied/EntityDied | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | HealthComponent with max/current HP, IsAlive | ❌ No ADR |
| _(placeholder)_ | TakeDamage consumes HitEvent from Event Bus | ADR-002 ✅ |
| _(placeholder)_ | Faction-aware damage application (no friendly fire) | ❌ No ADR |
| _(placeholder)_ | Death event published on HP ≤ 0 | ADR-002 ✅ |
| _(placeholder)_ | Healing support for future potions/regen | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/damage-health.md` are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Damage & Health Core | Integration | Draft | ADR-001, ADR-002 |

## Next Step

Implement story 001 after HD-002 (Hit Detection & Event Dispatch) is complete.
