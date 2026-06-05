# Epic: Hit Detection

> **Layer**: Foundation
> **System**: Hit Detection
> **GDD**: `design/gdd/hit-detection.md`
> **Architecture Module**: Hit Detection
> **Status**: Ready
> **Stories**: 3 (001 — Ready, 002 — Ready, 003 — Ready)

## Overview

Manages collision hitbox/hurtbox pairing between player projectiles and enemies, and between enemies and the player. Wraps the template's existing 3D trigger-based collision (`DamageEntity.OnTriggerEnter`, `MonsterEntity.OnTriggerEnter`) with a faction-aware registration system and outputs typed `HitEvent` to the Event Bus. Does not replace template collision — extends it with structured routing and cross-system event dispatch.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |
| ADR-002: Event Bus Contract | Publishes HitEvent to Event Bus for downstream consumers | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Faction-aware hitbox/hurtbox registration (Player/Enemy/Neutral) | ❌ No ADR |
| _(placeholder)_ | Wraps template OnTriggerEnter — never modifies vendor code | ❌ No ADR |
| _(placeholder)_ | Per-target hit cooldown (0.3s) prevents multi-hit | ❌ No ADR |
| _(placeholder)_ | Publishes typed HitEvent to Event Bus | ADR-002 ✅ |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/hit-detection.md` are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Hitbox/Hurtbox Registration & Faction System | Logic | Ready | ADR-001, ADR-002 |
| 002 | Hit Detection & Event Dispatch | Integration | Ready | ADR-002 |
| 003 | Per-Target Hit Cooldown | Logic | Ready | ADR-002 |

## Next Step

Implement stories in order from lowest to highest number.
