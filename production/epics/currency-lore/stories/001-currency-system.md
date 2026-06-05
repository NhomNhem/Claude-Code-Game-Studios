# Story 001: Currency System

- **Epic**: Currency & Lore
- **System**: Currency System
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-currency-001` | Earn/spend with server-authoritative validation hooks | ✅ ADR-001 |
| `TR-currency-002` | Consumes currency events from Event Bus | ✅ ADR-002 |
| `TR-currency-003` | GPM=300, PPH=2, PDR=1.2 constants for fraud cap | ❌ No ADR |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `ICurrencyService` registers as interface singleton in TinyRiftScope
- Delegates persistence to Save/Profile via `ModifyGoldAsync` / `ModifyShardsAsync`

**ADR-002 (Event Bus Contract):**
- Consumes `EntityDiedEvent` for currency drops from kills
- Publishes `CurrencyChangedEvent` for HUD/camp UI consumption

**Control Manifest (relevant rules):**
- Never access Save/Profile directly — use `IModifyPersistStateService` interface
- All currency mutations go through `ICurrencyService`
- Balance bounds validated by Save/Profile's `SaveDataValidator`

## Description

Implement the Currency System managing Gold (common) and Aether Shards (premium). Earns gold from enemy kills scaled by enemy tier and run time, with Aether Shards from elite/boss kills (guaranteed + RNG). Client-authoritative earnings with server sync via Save/Profile. Publishes `CurrencyChangedEvent` on balance change. Exposes `ICurrencyService` API for balance queries and spend operations.

## Design

```csharp
public interface ICurrencyService
{
    long GetGold();
    long GetShards();
    bool CanAfford(long goldCost, long shardCost);
    void ModifyGoldAsync(long delta);
    void ModifyShardsAsync(long delta);
    long GoldEarnedThisRun { get; }
    long ShardsEarnedThisRun { get; }
}
```

### Earning Rules

- Gold per kill: `baseGold + floor(runTimeSeconds × goldTimeScalar) + variance`
- Enemy tier base gold: Basic=5, Fast=3, Tank=12, Elite=50, Boss=200
- Elite: 33% chance of 1 Aether Shard (`ELITE_DROP_CHANCE = 0.33`)
- Boss: Guaranteed 1 Aether Shard + 20% chance of second (`PDR = 1.2`)
- Completion bonus: `zoneDepth × 200 + bossDefeated × 500 + floor(runTimeSeconds × 0.5)`

### Spend Rules

1. `CanAfford(cost)` check before any spend
2. Atomic dual-currency spend: both succeed or both rejected
3. Negative balance prevention via SaveDataValidator (`gold >= 0`, `premiumCurrency >= 0`)

### Fraud Detection Constants (references only — enforced server-side)

| Constant | Default | Purpose |
|----------|---------|---------|
| GPM (goldEarnedPerMinuteAvg) | 300 | Max expected gold/min |
| PPH (premiumPerHourAvg) | 2 | Max expected premium/hour |
| PDR (premiumDropRate) | 1.2 | Premium variance multiplier |

## Acceptance Criteria

1. **Gold from basic kill**: When `EntityDiedEvent` for a basic enemy fires, `GetGold()` increases by `baseGold(basic) + timeScalar`.
2. **Gold from elite kill**: When an elite dies, `GetGold()` increases by `baseGold(elite)`.
3. **Aether Shards from elite**: When an elite dies, `GetShards()` increases by 1 with probability `ELITE_DROP_CHANCE` (statistical over 1000+ events).
4. **Boss guarantees shard**: When the boss dies, `GetShards()` increases by exactly 1 (guaranteed).
5. **CanAfford returns true**: When `GetGold() = 1000`, `CanAfford(500, 0)` returns true.
6. **CanAfford returns false**: When `GetGold() = 200`, `CanAfford(500, 0)` returns false.
7. **Atomic dual-currency reject**: When gold is insufficient for a dual-currency spend, both are rejected — shards remain unchanged.
8. **Run-state tracking**: `GoldEarnedThisRun` and `ShardsEarnedThisRun` accumulate correctly over a run.
9. **CurrencyChangedEvent published**: Every balance mutation publishes `CurrencyChangedEvent` with correct `deltaGold`, `deltaShards`, and `source`.
10. **200 kills within 16ms**: Processing 200 `EntityDiedEvent` messages completes under a single frame budget.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/CurrencySystem/CurrencyServiceTests.cs`
- Per-kill earning calculations for all enemy tiers
- Spend validation (CanAfford, dual-currency atomicity)
- Event publishing (EntityDiedEvent → CurrencyChangedEvent)

## Dependencies

- **Event Bus** — Consumes `EntityDiedEvent`, publishes `CurrencyChangedEvent`
- **Save/Profile** — `ModifyGoldAsync`, `ModifyShardsAsync`, balance persistence, fraud detection constants

## Unlocks

- HUD (subscribes to `CurrencyChangedEvent` for real-time balance display)
- Hero Camp (reads `CanAfford()`, calls `ModifyXAsync(-cost)` for purchases)

## Risks

- **LOW**: GPM=300 may trigger false positives for high-skill players. Mitigation: GPM is server-side cap, not enforced client-side in MVP. Playtest data will inform tuning.
- **LOW**: Currency drift between client-authoritative balance and server sync. Mitigation: client balance is display-only; server balance is authoritative.
