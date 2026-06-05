# Epic: Foundation Infrastructure

> **Layer**: Foundation
> **Systems**: Game State Manager, Event Bus, Time System
> **GDDs**: `design/gdd/game-state-manager.md`, `design/gdd/event-bus.md`, `design/gdd/time-system.md`
> **Architecture Modules**: Game State Manager, Event Bus, Time System
> **Status**: In Progress
> **Stories**: 6 stories in `stories/` — see index below

## Overview

Implements three cross-cutting Foundation infrastructure systems that every other system depends on. Game State Manager provides a lightweight FSM for top-level phase transitions (Menu/InRun/Paused/etc.) and publishes changes via Event Bus. Event Bus provides typed publish/subscribe messaging decoupling all producers from consumers. Time System provides a unified time authority managing timeScale, cooldowns, hit-stop, and run timer. Together these form the backbone that all higher-layer systems communicate through.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Two-scope hierarchy: BackendLifetimeScope → TinyRiftScope. All custom systems register as interface singletons. | LOW — VContainer is third-party, bundled in template |
| ADR-002: Event Bus Contract | Typed `readonly record struct` events. Split interface pattern (IEventBus/ISubscriber). Reentrancy guard at depth 16. AOT via link.xml delegate preservation. | HIGH — IL2CPP delegate type stripping |
| ADR-004: Time System & Hit-Stop | TimeManager as sole authority over Time.timeScale. Cooldown registry. Pause-safe timing. Hit-stop owned by TimeManager. | LOW — Time APIs are stable in Unity 6 |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | GameStateManager maintains single active state | ❌ No ADR — TR registry needs population |
| _(placeholder)_ | GameStateManager publishes state-change events via Event Bus | ADR-002 ✅ |
| _(placeholder)_ | Event Bus supports typed readonly record struct events | ADR-002 ✅ |
| _(placeholder)_ | Event Bus has split interface (IEventBus + ISubscriber) | ADR-002 ✅ |
| _(placeholder)_ | Event Bus protects against reentrant publish up to depth 16 | ADR-002 ✅ |
| _(placeholder)_ | TimeManager is sole authority over Time.timeScale | ADR-004 ✅ |
| _(placeholder)_ | TimeManager provides cooldown registration and query API | ADR-004 ✅ |
| _(placeholder)_ | TimeManager provides GState-aware pause-safe timing | ADR-004 ✅ |
| _(placeholder)_ | All systems register in TinyRiftScope as interface singletons | ADR-001 ✅ |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from the three GDDs are verified
- All Logic and Integration stories have passing test files in `tests/`
- All Visual/Feel and UI stories have evidence docs with sign-off in `production/qa/evidence/`

## Story Index

| # | Title | Type | Priority | Story File | QA Verdict |
|---|-------|------|----------|------------|------------|
| 001 | GState Core State Machine | Logic | P0 | `stories/001-gstate-core-state-machine.md` | READY ✅ |
| 002 | Event Bus Core | Logic | P0 | `stories/002-event-bus-core.md` | READY ✅ |
| 003 | Time System Core | Logic | P0 | `stories/003-time-system-core.md` | READY ✅ |
| 004 | Hit-Stop | Logic | P1 | `stories/004-hit-stop.md` | READY ✅ |
| 005 | GState → Event Bus Integration | Integration | P0 | `stories/005-gstate-event-bus-integration.md` | READY ✅ |
| 006 | GState → Time System Integration | Integration | P0 | `stories/006-gstate-time-integration.md` | READY ✅ |

## Cross-Cutting Concerns

- All Foundation-layer systems register via VContainer in `TinyRiftScope` as interface singletons (per ADR-001). Individual stories do not re-declare this dependency.
- `ITimeProvider` / `ManualTimeProvider` / `UnityTimeProvider` in `Assets/_TinyRift/Tests/Helpers/` shared across Stories 003, 004, 006.
- TR registry (`docs/architecture/tr-registry.yaml`) is empty — all TR-IDs are placeholders. Must be backfilled before Production gate.
- Story 005 can be implemented in parallel with Story 003/004 (different dependency chains). Stories 003 → 004 → 006 are sequential.
