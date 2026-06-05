# Epic: Zone & World

> **Layer**: Core
> **Systems**: Zone Definition System, World State
> **GDDs**: `design/gdd/zone-definition-system.md`, `design/gdd/world-state.md`
> **Architecture Modules**: Zone Definition, World State
> **Status**: Ready
> **Stories**: Not yet created — run `/create-stories zone-world`

## Overview

Two data-driven systems defining the game's zone content and persistent world progression. Zone Definition System provides `ZoneDefinitionSO` ScriptableObject assets defining each zone's identity, wave composition tables, elite spawn rules, boss data, and environment cues — consumed by Wave Spawning, Audio, and VFX systems. World State maintains runtime registry of per-zone completion and restoration state, publishing `ZoneRestoredEvent` on victory for VFX/post-processing consumption.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Both register as interface singletons in TinyRiftScope | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | ZoneDefinitionSO ScriptableObjects with wave composition tables | ❌ No ADR |
| _(placeholder)_ | Zone audio ambience and environment cues | ❌ No ADR |
| _(placeholder)_ | World State tracks per-zone completion and restoration | ❌ No ADR |
| _(placeholder)_ | ZoneRestoredEvent published on zone victory | ❌ No ADR |
| _(placeholder)_ | World State loads/persists via Save/Profile | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from both GDDs are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | ZoneDefinitionSO | Config/Data | Ready | ADR-001 |
| 002 | World State | Integration | Ready | ADR-001 |

## Next Step

Run `/dev-story` on a zone & world story to begin implementation.
