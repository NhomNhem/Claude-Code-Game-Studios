# Boss Encounter System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (narrative context, elemental weaknesses, phase transition activity added)
> **Status**: Designed

> **System ID**: #26
> **Layer**: Gameplay
> **Priority**: MVP
> **Created**: 2026-05-29
> **Design Order**: 24
> **Depends on**: Enemy AI (#24), Zone Definition (#12), Status Effect (#18), Object Pooling (#4)
> **Depended by**: Wave Spawning (#25), World State (#13), Screen Shake (#27), VFX (#15)

## 1. Overview

The Boss Encounter System manages boss-specific combat — activation, phase transitions, attack patterns, and defeat detection. Each zone has a single boss encounter defined in its Zone Definition. The boss is a unique enemy with phased HP, phase-specific attack sets, and dramatic phase transitions. Boss defeat triggers zone victory.

## 2. Player Fantasy

The boss is the climax — a fight that tests everything your build can do. Each phase is a new puzzle: the boss changes its attacks, you adapt. Phase transitions are cinematic moments — the boss roars, the arena shifts, and you know the hardest part is coming. Defeating the boss is the most satisfying moment in a run.

## 3. Detailed Rules

**Architecture:**
- `IBossEncounterService` (interface) — injected via VContainer in `GameplayLifetimeScope`
- `BossEncounterService` — manages boss lifecycle, phase state, attack execution
- `BossRuntimeState`: `bool isActive`, `BossPhase currentPhase`, `float phaseHpRemaining`, `float totalHp`, `float attackCooldownTimer`
- Boss is a single entity (not pooled like normal enemies) — spawned from a dedicated boss prefab

**Activation:**
- Wave Spawning publishes `GameStateChangedEvent(InRun, InRun, BossContext.Triggered)` when boss wave is reached
- Boss Encounter subscribes to `BossContext.Triggered` context
- Remaining non-boss enemies are cleared from arena
- Boss intro delay (from `BossEncounterData.introDelay`) plays — camera focus, boss spawn VFX
- Boss spawns at designated boss position from Zone Definition
- `GameStateChangedEvent(InRun, InRun, BossContext.Active)` published

**Phases:**
- Each phase in `BossEncounterData.phases` defines: `hpThreshold` (0.0–1.0, percentage of total HP), `attackSet` (list of attack IDs), `phaseIntroDelay`
- Boss starts in Phase 0 (first phase in the list)
- Phase transitions trigger when boss HP drops below the next phase's `hpThreshold`
- On transition: boss becomes invulnerable for `phaseIntroDelay`, plays phase-change VFX, updates attack set
- Phase vulnerability window: boss takes 0 damage during transition (brief immunity)

**Attack Execution:**
- Each phase has an `attackSet` — IDs reference attack patterns defined in this system
- Boss attacks on a cooldown (per-attack cooldown, not per-phase)
- Attack cooldown decreases as phases advance (boss gets more aggressive)
- Attack types: `MeleeSwipe` (frontal cone), `RangedBurst` (projectile spread), `GroundSlam` (AoE around boss), `SummonAdds` (spawns 3-5 normal enemies), `Charge` (line AoE dash)
- Attack targets the nearest player

**Boss Defeat:**
- Boss HP reaches 0 → play death VFX → publish `EntityDiedEvent(BossId, PlayerId)`
- Publish `GameStateChangedEvent(InRun, Victory, ZoneId)`
- World State marks zone as restored
- Boss entity is despawned after death animation

**Boss Immunity:**
- Boss is immune to Stun (cannot be interrupted during attacks)
- Boss is immune to Freeze (cannot be rooted)
- Boss is affected by Burn DOT but at 50% effectiveness
- Status immunity configurable per-zone boss via `BossEncounterData`

**Phase Transition Activity:**
- During the brief invulnerability window, the player is NOT idle — a telegraphed expanding AoE ring forces repositioning, orbs spawn to collect for a small heal, or adds begin to stream in
- The transition is a gameplay beat, not a cutscene

**Elemental Weaknesses (per boss):**
- The Molten Core (Fire boss): weak to Ice (+25% damage), resists Fire (−25%), immune to Stun
- The Crystal Heart (Ice boss): weak to Fire (+25% damage), resists Ice (−25%), immune to Freeze
- The Final Echo (Lightning boss): no elemental weakness in MVP (resists all elements evenly), immune to Stun and Freeze, Burn at 50%

**Narrative Context:**
- The Molten Core: once the forge-heart of a civilization that burned itself out. Still radiates the last ambition of its creators.
- The Crystal Heart: the frozen core of a city that tried to preserve itself in crystalline stasis. The crystal remembers everything — and everyone it failed to save.
- The Final Echo: the lingering consciousness of the civilization's final moment. It doesn't attack with malice — it reenacts the catastrophe endlessly, trapped in its last memory.

**MVP Boss Count:**
- 1 boss per zone (3 total for MVP)
- Zone 1 (Fractured Pass): The Molten Core — fire boss, Phase 1 = melee + charge, Phase 2 = adds + AoE
- Zone 2 (Crystal Caverns): The Crystal Heart — ice boss, Phase 1 = ranged + walls, Phase 2 = shard rain
- Zone 3 (Ash Circle): The Final Echo — lightning boss, Phase 1 = charge + burst, Phase 2 = arena-wide arcs, Phase 3 = all patterns

## 4. Formulas

```
bossHpPerPhase = totalBossHp × (hpThreshold[n] - hpThreshold[n-1])
attackCooldown(phase) = baseCooldown × (1.0 - phaseIndex × 0.15)
phaseTransitionDuration = phaseIntroDelay + 0.5s (VFX)
```

Where:
- `totalBossHp` — from `BossEncounterData` (per boss, per zone)
- `hpThreshold[n]` — the HP percentage at which phase n starts (e.g., Phase 1 at 100%, Phase 2 at 50%)
- `baseCooldown` — from boss definition (e.g., 3.0s)
- `phaseIndex` — 0 for first phase, 1 for second, etc.

## 5. Edge Cases

- **If boss is null or missing config**: Boss trigger fires but no boss spawns. `GetBossEncounterData()` returns null → log error, skip boss, treat zone as incomplete (no victory trigger).
- **If player dies during phase transition** (boss invulnerable): Player death takes priority. Run ends (Defeat). Phase transition cancels.
- **If player kills boss via Burn DOT during invulnerability window**: Burn DOT reduced to 50% but still applies. If lethal, bypasses invulnerability. Acceptable edge case.
- **If boss has 0 phases defined**: Boss spawns with no attacks. Base stats only. Player kills boss with no challenge. Log warning.
- **If boss attack cooldown reaches 0**: Boss attacks every frame. Clamped to 0.2s minimum to prevent instant attacks.
- **If player retreats from zone during boss fight**: Boss despawns. Zone considered abandoned. Boss HP not saved.
- **If boss's remaining attacks list is empty** (all attacks on cooldown): Boss waits idle until an attack cooldown expires.

## 6. Dependencies

| System | ID | Direction | Notes |
|--------|----|-----------|-------|
| Zone Definition | #12 | Data | Reads `BossEncounterData`, phase configs |
| Game State | #1 | Consumer + Producer | Listens for boss trigger, publishes active/victory |
| Enemy AI | #24 | Consumer | Summoned adds use Enemy AI system |
| Status Effect | #18 | Data | Configures boss immunity per status |
| Object Pooling | #4 | Dependency | Boss is not pooled (unique), adds are pooled |
| VFX System | #15 | Consumer | Phase transition VFX, death VFX |
| Screen Shake | #27 | Consumer | Camera shake on boss attacks |

## 7. Tuning Knobs

| Knob | Default | Range | Effect When Max | Effect When Min | Owner |
|------|---------|-------|-----------------|-----------------|-------|
| Base attack cooldown | 3.0s | 1.5–6.0s | Slow, telegraphed fights | Relentless attacks | BossDefinition |
| Phase cooldown reduction | 0.15/phase | 0.05–0.3 | Drastic pace increase late | Consistent pace throughout | BossDefinition |
| Burn DOT effectiveness | 50% | 25–100% | DOT still viable vs bosses | DOT worthless vs bosses | BossDefinition |
| Phase transition invulnerability | 0.5s | 0.0–2.0s | Safe transition window | Boss vulnerable during transition | BossDefinition |
| Boss intro delay | 2.0s | 1.0–5.0s | Cinematic build-up | Gets to the fight fast | ZoneDefinition |

## 8. Acceptance Criteria

1. **Boss spawns on trigger** — When `BossContext.Triggered` fires, boss spawns at designated position after intro delay.
2. **Phase transitions at HP threshold** — When boss HP drops below phase threshold, phase transition triggers with invulnerability window.
3. **Attack set changes per phase** — Each phase has its own attack set; boss only uses attacks from current phase.
4. **Attack cooldown decreases per phase** — Boss attacks more frequently in later phases.
5. **Boss immune to Stun/Freeze** — Status system checks boss immunity before applying Stun or Freeze.
6. **Burn DOT at reduced effectiveness** — Burn deals 50% damage to boss (configurable).
7. **Boss defeat triggers victory** — When boss HP reaches 0, `GameStateChangedEvent(InRun, Victory)` is published.
8. **Summon Adds spawns enemies** — When boss uses SummonAdds attack, normal enemies spawn via Enemy AI.
9. **Missing boss config handled** — If `GetBossEncounterData()` returns null, boss is skipped with error log.
10. **Boss despawns on zone exit** — If player leaves zone during boss fight, boss despawns.
11. **Phase transition VFX plays** — On phase change, transition VFX plays and boss is briefly invulnerable.
12. **Zone victory only via boss defeat** — Zone cannot complete without boss being defeated.
