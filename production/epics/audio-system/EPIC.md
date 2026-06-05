# Epic: Audio System

> **Layer**: Core
> **System**: Audio System
> **GDD**: `design/gdd/audio-system.md`
> **Architecture Module**: Audio System
> **Status**: Ready
> **Stories**: 2 stories in `stories/` — see index below

## Overview

Wraps the template's `AudioManager` and `SoundEffectsPool` in a VContainer-registered service layer that dispatches all game audio. Subscribes to 7 Event Bus event types (`GameStateChanged`, `DamageDealt`, `EntityDied`, `LevelUp`, `CurrencyChanged`, `LoreFragmentCollected`, `ZoneRestored`) and maps each to the appropriate SFX or music action. Manages music crossfade across GState transitions, resolves per-zone ambience via `IZoneAudioProvider`, and plays skill-specific combat SFX via string audio keys from Skill Data.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers as interface singleton in TinyRiftScope | LOW |
| ADR-002: Event Bus Contract | Consumes 7 event types from Event Bus | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Subscribes to Event Bus events for audio dispatch | ADR-002 ✅ |
| _(placeholder)_ | Manages music crossfade across GState transitions | ❌ No ADR |
| _(placeholder)_ | Resolves per-zone ambience via IZoneAudioProvider | ❌ No ADR |
| _(placeholder)_ | Plays skill-specific SFX via string audio keys from Skill Data | ❌ No ADR |

## Story Index

| # | Title | Type | Priority | Story File | QA Verdict |
|---|-------|------|----------|------------|------------|
| 001 | Event Bus Consumer & SFX Dispatch | Integration | P0 | `stories/001-event-bus-consumer-sfx.md` | READY |
| 002 | Music Crossfade & Zone Ambience | Integration | P1 | `stories/002-music-crossfade-ambience.md` | READY |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from `design/gdd/audio-system.md` are verified
- All Logic and Integration stories have passing test files in `tests/`
