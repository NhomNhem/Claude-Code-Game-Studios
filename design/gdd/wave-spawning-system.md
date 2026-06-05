# Wave Spawning System

> **Creative Director Review (CD-GDD-ALIGN)**: APPROVED — 2026-05-29 (pre-wave delay P3 guidance added)
> **Status**: Designed

> **System ID**: #25
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 23
> **Depends on**: Zone Definition (#12), Game State (#1), Object Pooling (#4), Enemy AI (#24)
> **Depended by**: Run Manager, World State (#13)

## 1. Overview

The Wave Spawning System drives combat progression within a zone. It reads the zone's wave table from Zone Definition, spawns enemies per wave (with pre-wave delay, wave duration, and spawn group configuration), detects wave completion (all enemies killed or timer expired), advances to the next wave, and triggers the boss encounter when the boss wave is reached.

## 2. Player Fantasy

Each wave is a distinct combat beat. The pre-wave delay builds tension, enemies stream in according to the zone's composition, and clearing a wave feels like overcoming a chapter. Waves build in intensity — more enemies, tougher types — culminating in the boss. The pacing is authored per zone, so each zone has its own rhythm.

## 3. Detailed Rules

**Architecture:**
- `IWaveSpawningService` (interface) — injected via VContainer in `GameplayLifetimeScope`
- `WaveSpawningService` — owns wave progression state, spawns enemies via Enemy AI pool
- `WaveRuntimeState`: `int currentWaveIndex`, `float waveTimer`, `int remainingEnemyCount`, `ZoneId currentZone`, `bool bossTriggered`

**Wave Progression Loop:**
1. On zone entry (`GameStateChangedEvent(InRun, currentZone)`): initialize wave state, start pre-wave delay for wave 0
2. Pre-wave delay: no enemies visible, countdown UI optional
3. Spawn wave: iterate `WaveTableEntry.spawnGroups`, spawn each group's enemies via Object Pooling at configured spawn positions
4. Wave active: enemies fight. Wave timer counts down from `WaveTableEntry.duration`
5. Wave completion: all enemies killed OR wave timer expires → whichever comes first
6. If timer expires, remaining enemies are NOT despawned (they continue fighting). Next wave's pre-wave delay starts, and new enemies spawn alongside survivors.
7. If all enemies killed before timer: wave completes early. Short inter-wave pause (1s), then next wave begins.
8. Repeat until `currentWaveIndex >= waveCount` or boss wave triggers

**Pre-wave delay P3 guidance:** Pre-wave delay should rarely exceed 1.5s to avoid dead-time. Longer delays (>1.5s) are reserved for narrative beats (zone entry, boss introduction) where tension serves P1.

**Boss Trigger:**
- When `currentWaveIndex == bossEncounter.triggerWave`: publish `GameStateChangedEvent(InRun, InRun, BossContext.Triggered)` instead of spawning wave enemies
- Boss Encounter system handles the rest
- After boss defeat: wave progression stops, zone is considered complete

**Spawn Positions:**
- Each `SpawnGroup` has a `spawnPattern` field: `Perimeter` (evenly spaced around arena edge), `Cluster` (tight group at random location), `Wave` (sequential from one edge)
- Positions are computed relative to the arena bounds (read from Zone Definition's arena config)
- Enemies are spawned via `ObjectPool.Get(enemyPrefabKey, position, rotation)`, then activated by Enemy AI system

**Wave State Persistence:**
- Wave state is per-run, not persisted to save file
- On zone transition (retreat, death): wave state is discarded
- On re-entering a zone (if allowed): wave state starts fresh from wave 0

## 4. Formulas

```
waveEnemyCount(waveIndex) = sum(spawnGroup[g].count for each group in waveTable[waveIndex].spawnGroups)
preWaveDelay(waveIndex) = waveTable[waveIndex].preWaveDelay
waveDuration(waveIndex) = waveTable[waveIndex].duration
```

No additional formulas. Wave composition is authored per-zone by level designers.

## 5. Edge Cases

- **If wave timer expires and enemies remain**: Timer expiry does not despawn enemies. Survivors persist into next wave. This creates compounding pressure across waves.
- **If all spawnGroups have count = 0**: Wave spawns 0 enemies. Wave completes immediately after pre-wave delay (0s wave duration). Next wave starts immediately. Log a warning.
- **If boss trigger wave is reached but bossEncounter is null**: Log error, skip boss wave, advance to next wave. Zone continues without boss.
- **If zone has no wave table entries** (misconfigured): Log error on zone entry. No enemies spawn. Wave progression immediately completes. Zone ends with no combat.
- **If player retreats mid-wave**: Wave state discarded. Zone considered abandoned. Enemies despawned.
- **If elite spawn probability check triggers for a wave**: Elite enemies are spawned alongside regular enemies as part of the wave composition (handled by Zone Definition's elite spawn rules, not Wave Spawning).

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Zone Definition | #12 | Data | Reads `WaveTableEntry`, boss trigger config |
| Game State | #1 | Consumer | Listens for zone entry/exit, publishes boss trigger |
| Object Pooling | #4 | Dependency | Spawns enemies from pool by key |
| Enemy AI | #24 | Trigger | Activates spawned enemy instances |
| Boss Encounter | #26 | Trigger | Publishes boss trigger event on boss wave |
| Time System | #6 | Dependency | Pre-wave delay timer, wave duration timer |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Inter-wave pause (early clear) | 1.0s | 0.5–3.0s | Breather between waves | Relentless pace | WaveSpawningService |
| Wave timer expiry behavior | Keep enemies | Keep/Despawn | Compounding pressure | Clean slate each wave | WaveSpawningService |

## 8. Acceptance Criteria

1. **Wave spawns on zone entry** — When entering a zone, wave 0's pre-wave delay starts, then enemies spawn per the wave table.
2. **Wave completes on kill-all** — When all enemies in a wave are killed, the wave completes and the next wave begins after inter-wave pause.
3. **Wave completes on timer expiry** — When wave duration expires, the wave completes and the next wave begins (surviving enemies persist).
4. **Boss triggers at configured wave** — When `currentWaveIndex == bossEncounter.triggerWave`, boss trigger event is published.
5. **Spawn positions match pattern** — Enemies spawn according to their group's `spawnPattern` (Perimeter, Cluster, Wave).
6. **All enemies despawn on zone exit** — When leaving the zone, all active enemies return to pool.
7. **Wave state resets on re-entry** — On re-entering a zone, wave progression starts fresh from wave 0.
8. **Empty wave handled gracefully** — Wave with 0 spawns completes immediately with a logged warning.
9. **Missing boss handled gracefully** — Boss trigger wave with no boss config logs error and advances to next wave.
10. **Compounding waves work** — When timer expires, surviving enemies remain and next wave's enemies spawn alongside them.
