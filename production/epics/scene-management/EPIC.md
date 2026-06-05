# Epic: Scene Management

> **Layer**: Core
> **System**: Scene Manager
> **GDD**: `design/gdd/scene-manager.md`
> **Architecture Module**: Scene Manager
> **Status**: Ready
> **Stories**: Not yet created — run `/create-stories scene-management`

## Overview

Owns the mapping between `GameState` transitions and Unity scene lifecycle. Receives `GameStateChanged` events from the Event Bus, determines which scene to load based on target state, and orchestrates async scene loading via `SceneManager.LoadSceneAsync`. Supports additive scene loading for zone transitions. Provides loading progress to the Loading/Transition System. Rejects invalid loading requests (double-loads, missing scenes).

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Maps GameState transitions to scene loads/unloads | ❌ No ADR |
| _(placeholder)_ | Supports additive scene loading for zone transitions | ❌ No ADR |
| _(placeholder)_ | Provides loading progress to Loading/Transition System | ❌ No ADR |
| _(placeholder)_ | Rejects invalid loading requests (double-loads, missing scenes) | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/scene-manager.md` are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Scene Load/Unload Core | Logic | Ready | ADR-001 |
| 002 | Error Handling & Safety | Logic | Ready | ADR-001 |
| 003 | Activation & Completion Flow | Logic | Ready | ADR-001 |
| 004 | Preloading & Edge Cases | Logic | Ready | ADR-001 |

## Next Step

Run `/dev-story` on a scene management story to begin implementation.
