# Epic: Network & Object Pooling

> **Layer**: Foundation
> **Systems**: Network Manager, Object Pooling
> **GDDs**: `design/gdd/network-manager.md`, `design/gdd/object-pooling.md`
> **Architecture Modules**: Network Manager, Object Pooling
> **Status**: Ready
> **Stories**: 4 (001 — Ready, 002 — Ready, 003 — Ready, 004 — Ready)

## Overview

Two infrastructure systems that serve all higher layers. Network Manager manages the WebSocket connection lifecycle between client and tiny-rift-server, wrapping the template's `IBackendService` with a connection state machine, auto-reconnect, and heartbeat health check. Object Pooling pre-allocates and recycles frequently-spawned GameObjects (projectiles, enemies, VFX, damage numbers) via `UnityEngine.Pool.ObjectPool<T>`, preventing GC spikes in the combat hot path.

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|-----------------|-------------|
| ADR-001: VContainer DI Architecture | Both register as interface singletons in TinyRiftScope | LOW |
| ADR-005: Object Pooling Strategy | Wraps `ObjectPool<T>` in PoolManager with PoolProfile config. IPoolable lifecycle. AOT preservation via static type forcing. ClearAll() on scene transitions. | HIGH — IL2CPP stripping of ObjectPool<T> generics |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| _(placeholder)_ | Network Manager wraps IBackendService (WebSocketSqlBackendService) | ❌ No ADR |
| _(placeholder)_ | Connection state machine with auto-reconnect and heartbeat | ❌ No ADR |
| _(placeholder)_ | PoolManager wraps ObjectPool<T> with prefab-keyed pools | ADR-005 ✅ |
| _(placeholder)_ | PoolProfile ScriptableObjects for pre-warm counts | ADR-005 ✅ |
| _(placeholder)_ | IPoolable lifecycle callbacks on pooled objects | ADR-005 ✅ |
| _(placeholder)_ | AOT preservation for all ObjectPool<T> concrete types | ADR-005 ✅ |

## Definition of Done

This epic is complete when:
- All stories are implemented, reviewed, and closed via `/story-done`
- All acceptance criteria from both GDDs are verified
- All Logic and Integration stories have passing test files in `tests/`
- IL2CPP build compiles with all ObjectPool<T> types preserved

## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | Connection State Machine | Logic | Ready | ADR-001 |
| 002 | Reconnection & Error Handling | Logic | Ready | ADR-001 |
| 003 | PoolManager Core | Logic | Ready | ADR-001, ADR-005 |
| 004 | Pool Growth, Safety & AOT Preservation | Logic | Ready | ADR-001, ADR-005 |

## Next Step

Implement stories in order from lowest to highest number, interleaving Network and Pooling as dependencies allow.
