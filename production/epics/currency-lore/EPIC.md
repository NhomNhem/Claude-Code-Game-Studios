# Epic: Currency & Lore

> **Layer**: Core
> **Systems**: Currency System, Lore Fragment System
> **GDDs**: `design/gdd/currency-system.md`, `design/gdd/lore-fragment-system.md`
> **Architecture Modules**: Currency System, Lore Fragment
> **Status**: Ready
> **Stories**: 2 stories in `stories/` — see index below

## Overview

Two data-tracking systems that respond to combat events. Currency System manages Gold (common) and Aether Shards (premium/rare) earned from enemy kills and elite/boss kills — client-authoritative earnings with server sync, basic balance bounds in MVP, full server validation deferred to Alpha. Lore Fragment System auto-collects memory fragments on elite/boss death (if not already collected), persists via Save/Profile, publishes collection events for HUD toasts and VFX ripple effects, and provides read-only query layer for Codex UI.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Both register as interface singletons in TinyRiftScope | LOW |
| ADR-002: Event Bus Contract | Both consume events (EntityDiedEvent, etc.) from Event Bus | LOW |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Gold earned from enemy kills scaled by enemy tier | ❌ No ADR |
| _(placeholder)_ | Aether Shards from elite/boss kills (guaranteed or rare) | ❌ No ADR |
| _(placeholder)_ | Client-authoritative with server sync via Save/Profile | ❌ No ADR |
| _(placeholder)_ | Lore fragment auto-collected on elite/boss death | ❌ No ADR |
| _(placeholder)_ | Lore collection event published for HUD toast and VFX | ADR-002 ✅ |
| _(placeholder)_ | Codex query layer for collected fragments | ❌ No ADR |

## Story Index

| # | Title | Type | Priority | Story File | QA Verdict |
|---|-------|------|----------|------------|------------|
| 001 | Currency System | Integration | P0 | `stories/001-currency-system.md` | READY |
| 002 | Lore Fragment System | Integration | P1 | `stories/002-lore-fragment-system.md` | READY |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from both GDDs are verified
- All Logic and Integration stories have passing test files in `tests/`
