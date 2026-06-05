# Epic: Enemy AI

> **Layer**: Gameplay
> **System**: Enemy AI
> **GDD**: `design/gdd/enemy-ai.md`
> **Architecture Module**: Enemy AI
> **Status**: Stories Not Ready
> **Stories**: 1 (001 — Draft)

## Overview

Implements basic enemy behaviors on top of the template's `MonsterEntity`, `MonsterMovement`, and existing enemy FSM. Starts with basic chase AI: detect nearest player, move toward, attack when in range. Designed to be configurable via ScriptableObject (detection range, move speed, attack range) so designers can tune per enemy type without code changes.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Configs resolve via VContainer; AIs are MonoBehavior components | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Enemy detects nearest player within detection range | ❌ No ADR |
| _(placeholder)_ | Enemy moves toward detected player | ❌ No ADR |
| _(placeholder)_ | Enemy attacks when within attack range | ❌ No ADR |
| _(placeholder)_ | Enemy idles/patrols when no player detected | ❌ No ADR |
| _(placeholder)_ | All parameters configurable via EnemyAIConfig SO | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/enemy-ai.md` are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Basic Chase AI | Logic | Draft | ADR-001 |

## Next Step

Implement story 001 after Damage & Health epic exists and basic entity spawning is available.
