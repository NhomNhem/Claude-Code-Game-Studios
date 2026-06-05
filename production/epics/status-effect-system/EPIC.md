# Epic: Status Effect System

> **Layer**: Core
> **System**: Status Effect System
> **GDD**: `design/gdd/status-effect-system.md`
> **Architecture Module**: Status Effect
> **Status**: Ready
> **Stories**: 2 stories in `stories/` — see index below

## Overview

Manages elemental status conditions applied to enemies (and potentially the player) when damage of a matching element lands. Fire burns (DoT), Ice slows/freezes (movement speed reduction + immobilize), Lightning stuns (action lock). Effects are duration-based with tick timers managed by the Time System. Exposes `IStatusEffectService` for applying statuses, querying active statuses per entity, and clearing on entity death or scene transition.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |
| ADR-002: Event Bus Contract | Consumes DamageDealtEvent to resolve status effects by element type | LOW |
| ADR-004: Time System | Uses ITimeManager for tick countdown and duration tracking | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Fire applies DoT status (burn) | ❌ No ADR |
| _(placeholder)_ | Ice applies slow/freeze status | ❌ No ADR |
| _(placeholder)_ | Lightning applies stun status | ❌ No ADR |
| _(placeholder)_ | Status effects are duration-based with tick timers | ADR-004 ✅ |
| _(placeholder)_ | Exposes IStatusEffectService for apply/query/clear | ❌ No ADR |
| _(placeholder)_ | Consumes DamageDealtEvent to resolve element→status mapping | ADR-002 ✅ |

## Story Index

| # | Title | Type | Priority | Story File | QA Verdict |
|---|-------|------|----------|------------|------------|
| 001 | Status Effect Service Core | Logic | P0 | `stories/001-status-effect-service-core.md` | READY |
| 002 | Elemental Status Implementations | Integration | P0 | `stories/002-elemental-status-implementations.md` | READY |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/status-effect-system.md` are verified
- All Logic and Integration stories have passing test files in `tests/`
