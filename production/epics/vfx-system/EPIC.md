# Epic: VFX System

> **Layer**: Core
> **System**: VFX System
> **GDD**: `design/gdd/vfx-system.md`
> **Architecture Module**: VFX System
> **Status**: Ready
> **Stories**: 2 stories in `stories/` — see index below

## Overview

Owns all particle effects, non-UI visual feedback, and screen-space secondary effects (color sweeps, bursts, trails). Consumes events from the Event Bus and spawns/pre-scripted VFX sequences using a pooled object model. Elemental VFX are a core identity — fire scorches, ice fractures, lightning arcs. Wraps Unity's Particle System and handles effect lifecycle, pooling via PoolManager, and intensity scaling. HIGH engine risk due to URP 17.3 RenderGraph replacing CommandBuffer for custom passes.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |
| ADR-002: Event Bus Contract | Consumes events from Event Bus for VFX dispatch | LOW |
| ADR-005: Object Pooling Strategy | Uses PoolManager for pooled VFX controller lifecycle | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Consumes Event Bus events for VFX spawning | ADR-002 ✅ |
| _(placeholder)_ | Elemental VFX library (fire, ice, lightning, blood, rift) | ❌ No ADR |
| _(placeholder)_ | Uses PoolManager for pooled VFX lifecycle | ADR-005 ✅ |
| _(placeholder)_ | Handles effect lifecycle with intensity scaling | ❌ No ADR |
| _(placeholder)_ | Compatible with URP 17.3 RenderGraph pipeline | ❌ No ADR |

## Story Index

| # | Title | Type | Priority | Story File | QA Verdict |
|---|-------|------|----------|------------|------------|
| 001 | VFX Event Consumer & Pooled Lifecycle | Integration | P0 | `stories/001-vfx-event-consumer-pooled-lifecycle.md` | READY |
| 002 | Elemental VFX Library | Visual/Feel | P1 | `stories/002-elemental-vfx-library.md` | READY |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/vfx-system.md` are verified
- All Logic and Integration stories have passing test files in `tests/`
