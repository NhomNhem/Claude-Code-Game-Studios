# Epic: Input System

> **Layer**: Foundation
> **System**: Input System
> **GDD**: `design/gdd/input-system.md`
> **Architecture Module**: Input System
> **Status**: Ready
> **Stories**: 4 stories — see below

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | InputRouter Core — Action Maps & Movement | Logic | Ready | ADR-003 |
| 002 | Skill Activation & Hold-to-Aim | Logic | Ready | ADR-003 |
| 003 | Pause Toggle & Menu Navigation | Integration | Ready | ADR-003 |
| 004 | Edge Cases — Device Disconnect, Rebinds, State Safety | Logic | Ready | ADR-003 |

## Overview

Wraps Unity Input System 1.19.0 in a custom `InputRouter` service that abstracts keyboard/mouse, gamepad, and touch into logical game actions (Move, Aim, UseSkill, Pause, Interact). Manages three action maps (Gameplay/Menu/Camp) switched by GState via Event Bus subscription. Exposes `IInputRouter` interface consumed by CharacterEntity and UI. Never uses legacy Input class or template input controllers.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |
| ADR-003: Input System & InputRouter Wrapper Pattern | Wraps InputActionAsset in InputRouter. Three action maps switched by GState. Legacy Input banned. Exposes IInputRouter. | HIGH — Input System 1.19.0 is post-cutoff |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | InputRouter translates physical input to logical game actions | ADR-003 ✅ |
| _(placeholder)_ | Three action maps (Gameplay/Menu/Camp) switched by GState | ADR-003 ✅ |
| _(placeholder)_ | Supports KBM, gamepad, and touch input | ADR-003 ✅ |
| _(placeholder)_ | Never uses legacy Input class | ADR-003 ✅ |
| _(placeholder)_ | Exposes IInputRouter interface | ADR-003 ✅ |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/input-system.md` are verified
- All Logic and Integration stories have passing test files in `tests/`
- All Visual/Feel and UI stories have evidence docs with sign-off in `production/qa/evidence/`

## Next Step

Run `/story-readiness` on each story, then implement via `/dev-story` starting with Story 001.
