# Epic: Skill Data System

> **Layer**: Foundation
> **System**: Skill Data System
> **GDD**: `design/gdd/skill-data-system.md`
> **Architecture Module**: Skill Data System
> **Status**: Ready
> **Stories**: 3 stories in `stories/` — see index below

## Overview

Defines the data configuration layer for every skill in the game. Each skill is a `SkillDefinition` ScriptableObject containing a unique ID, element type, rarity tier, cooldown, damage parameters, orbit/burst behavior flags, upgrade definitions, VFX profile references, and audio cue keys. Skills are authored by designers as assets and referenced by string ID throughout the codebase — never as runtime types from higher layers (C3 constraint). Exposes `ISkillRegistry` for runtime queries. Blocks 11 downstream dependents.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Skills defined as ScriptableObject assets with unique ID | ❌ No ADR |
| _(placeholder)_ | Skills referenced by string ID, never runtime types | ❌ No ADR |
| _(placeholder)_ | Exposes ISkillRegistry for runtime queries | ❌ No ADR |
| _(placeholder)_ | Upgrade definitions and VFX profiles use pure data refs (C3) | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/skill-data-system.md` are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Title | Type | Priority | Story File |
|---|-------|------|----------|------------|
| 001 | SkillDefinition ScriptableObject Data Schema | Logic + Editor | P0 | `stories/001-skill-definition-schema.md` |
| 002 | SkillRegistry — Lookup, Validation & Instance Lifecycle | Logic | P0 | `stories/002-skill-registry.md` |
| 003 | SkillInstance C3 Compliance & Serialization | Integration | P1 | `stories/003-skill-instance-serialization.md` |
