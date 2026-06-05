# Epic: Orbit Combat

> **Layer**: Feature (Gameplay)
> **System**: Orbit Combat System
> **GDD**: `design/gdd/orbit-combat-system.md`
> **Architecture Module**: Orbit Combat
> **Status**: Active
> **Stories**: Not yet created — run `/create-stories orbit-combat`

## Overview

Manages passive orbit-style skills — projectiles that rotate around the player and auto-hit enemies on contact. Each orbit skill creates an `OrbitRing` (runtime container) with evenly-spaced pooled `OrbitProjectile` instances rotating at configurable speed and radius. Orbits activate on draft (no cooldown, no mana), persist until removed, and operate as late-update geometric positioning. Hit detection uses trigger colliders on each projectile publishing `HitEvent` without consuming the projectile. Multiple orbit skills stack independently up to a configurable max (MVP: 5, FIFO replacement). Orbits clear on zone transition and re-spawn from Build State on zone entry.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Registers `IOrbitCombatService` as singleton in TinyRiftScope via `GameplayLifetimeScope` | LOW |
| ADR-005: Object Pooling | `OrbitProjectile` prefabs are pooled via `PoolManager`, implement `IPoolable` | LOW |

> **Note**: No dedicated Orbit Combat ADR exists yet. Architecture recommends ADR-008 "Orbit Combat & Targeting Priority" (TRs: orbit-001–005) before Feature-layer implementation. See `docs/architecture/architecture.md:259`.

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| TR-orbit-001 | Passive orbital auto-attack with targeting priority | ❌ No ADR |
| TR-orbit-002 | Orbit rotation speed and projectile spawning | ❌ No ADR |
| TR-orbit-003 | Uses ObjectPool for projectile pooling | ADR-005 |
| ❌ Untraced | Per-enemy hit cooldown (0.3s per projectile per enemy) | ❌ No ADR |
| ❌ Untraced | Multiple orbit skills stack independently (up to max) | ❌ No ADR |
| ❌ Untraced | Upgrade changes take effect on orbit rings in real time | ❌ No ADR |
| ❌ Untraced | Orbit cleared on zone transition, re-spawned on entry | ❌ No ADR |
| ❌ Untraced | Max orbit limit enforced (FIFO replacement) | ❌ No ADR |
| ❌ Untraced | Zero projectile count logs warning, does not crash | ❌ No ADR |
| ❌ Untraced | Orbit removal despawns all projectiles for that ring | ❌ No ADR |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All 13 acceptance criteria from `design/gdd/orbit-combat-system.md` are verified
- All Logic and Integration stories have passing test files in `tests/`

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Orbit Ring Core | Logic | Ready | ADR-008, ADR-001, ADR-005 |
| 002 | Hit Cooldown & Multiple Rings | Logic | Ready | ADR-008 |
| 003 | Upgrades & Real-Time Changes | Integration | Ready | ADR-008 |
| 004 | Orbit Lifecycle & Transitions | Integration | Ready | ADR-008 |

## Next Step

Run `/story-readiness production/epics/orbit-combat/stories/001-orbit-ring-core.md` then `/dev-story 001` to begin implementation.
