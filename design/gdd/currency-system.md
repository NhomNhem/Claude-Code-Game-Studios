# Currency System

> **Status**: Designed (section-by-section approved 2026-05-27)
> **Design Order**: #11 (MVP)
> **Category**: Economy
> **Layer**: Core
> **Depends On**: Save/Profile Persistence (#10), Network Manager (#7)
> **Depended On By**: Hero Camp Progression (#28), Run Completion (#36), HUD (#30), Camp Menu UI (#32), Server Economy Validation (#41, deferred to Alpha)
> **Formulas referenced by**: Save/Profile Persistence — fraud detection (GPM, PPH, PDR, startingGold, startingPremium)

---

## 1. Overview

The Currency System manages two persistent currencies — **Gold** (common) and **Aether Shards** (premium/rare) — from earning through spend. It is a pure data-tracking layer with no UI of its own:

- **Gold** — earned from every enemy kill, scaled by enemy tier and run time. The primary progression resource for Hero Camp upgrades, zone unlocks, and hero unlocks (MVP scope).
- **Aether Shards** — earned as guaranteed or rare drops from elite and boss kills. The scarce resource gating premium content (premium hero unlocks, premium zone unlocks, signature upgrades).

The system is client-authoritative for earnings with server-synced balances (via Save/Profile). Full server-side fraud validation is deferred to the Server Economy Validation system (Alpha tier). In MVP, the Save/Profile system provides basic balance bounds through its `maxBalanceGold` and `maxPremiumCurrency` formulas.

The Currency System:
- Tracks current gold and aether shard balances (read from Save/Profile on load)
- Receives earning events from the Event Bus (`EntityDiedEvent` → currency drop calculation)
- Publishes `CurrencyChangedEvent` on the Event Bus for HUD/camp UI consumption
- Exposes an API: `GetBalance(currencyType)`, `ModifyGoldAsync(delta)`, `ModifyShardsAsync(delta)`, `CanAfford(goldCost, shardCost)`
- Delegates all persistence to Save/Profile via `ModifyGoldAsync` / `ModifyPremiumCurrencyAsync`
- Prepares `goldEarnedThisRun` and `premiumCurrencyEarnedThisRun` deltas for Save/Profile's run-state tracking

---

## 2. Player Fantasy

**Gold fantasy**: "Every kill fills the pot. Every run, even a failed one, inches me toward the next upgrade." Gold is the steady, reliable progression currency — the feeling of consistent forward momentum. The HUD counter ticks up smoothly during runs, and the Hero Camp shows clear price tags within reach after 1-3 runs.

**Aether Shards fantasy**: "That elite kill GLOWED purple — I got a Shard!" Aether Shards are the excitement moments. They drop rarely and unpredictably, creating a dopamine hit when they appear. Saving 3-5 shards feels like collecting treasure. Spending them is a meaningful commitment — once spent, you're committed to earning more. Each shard feels earned, not bought.

**Spend satisfaction**: When the player buys an upgrade, the currency drops with a satisfying spend animation (owned by HUD), the upgrade takes effect immediately, and the price tags for remaining upgrades become visible. No "you need 5 more gold" frustration — gold costs are designed so that 1-2 successful runs always earn enough for the next meaningful purchase. Aether Shard costs are few, visible from the start, and achievable within 5-10 MVP runs.

**Anti-grind**: Per the anti-pillar (game-concept.md:152-155), the economy is NOT a live-ops grind. No daily quests, no FOMO timers, no "come back tomorrow" mechanics. Gold flows freely from playing. Premium scarcity comes from run difficulty, not time gates.

---

## 3. Detailed Rules

### 3.1 Currency Types

| Currency | JSON Field | Type | Category | MVP Sinks | Source |
|----------|-----------|------|----------|-----------|--------|
| Gold | `gold` | long | Common | Hero Camp upgrades, zone unlocks, hero unlocks | Enemy kills, run completion, rare drops |
| Aether Shards | `premiumCurrency` | long | Premium | Premium hero/zone unlocks, signature upgrades | Elite/boss kills (guaranteed + RNG) |

### 3.2 Earning Rules

#### Gold Sources (per run)

1. **Basic enemy kills**: Every enemy kill drops gold. Amount per kill increases with run duration.
2. **Elite kills**: Guaranteed gold bonus on kill (higher than basic).
3. **Boss kills**: Large gold bonus on kill.
4. **Run completion bonus**: Gold awarded when the run ends (Defeat or Victory), based on zone depth and boss kills.
5. **Offline earnings**: Gold simulated based on elapsed time away (formula in Save/Profile Persistence GDD Section 4). Applied silently on reconnection.

#### Aether Shard Sources (per run)

1. **Elite kills**: Guaranteed small chance of 1 Aether Shard (not every elite). Design intent: ~1 shard per 2-3 elite encounters.
2. **Boss kills**: Guaranteed 1 Aether Shard + small chance of a second (via PDR variance).
3. **Rare drops**: Very small chance from any enemy, amplified by PDR. Design intent: a rare surprise, not a reliable source.
4. **Run completion bonus**: Small chance based on boss defeated (not amount-based — a single bonus roll).

**No other premium sources in MVP.** No login bonuses, no quests, no purchases, no ads. The player earns Aether Shards purely through gameplay.

### 3.3 Drop Timing

Gold and Aether Shards are credited immediately on kill (gold counter updates per-frame). The Event Bus fires `EntityDiedEvent` → Currency System calculates drop → calls `CurrencyChangedEvent` → HUD counter animates. No loot pickup, no collection — the currency just appears.

At run end, the cumulative `goldEarnedThisRun` and `premiumCurrencyEarnedThisRun` are handed to Save/Profile for persistence via `RunStateSaveData`.

### 3.4 Spend Rules

1. **Balance check**: Before any spend, the requesting system calls `CanAfford(cost)`. If false, the spend is rejected silently (the UI layer handles affordance — greying out buttons, showing red text).
2. **Spend API**: The system that owns the purchase (e.g., Hero Camp Progression for upgrades) calls `ModifyGoldAsync(-cost)` or `ModifyShardsAsync(-cost)`.
3. **Negative balance prevention**: The Save/Profile `SaveDataValidator` rejects negative balances (`gold >= 0`, `premiumCurrency >= 0`). If a spend would cause negative, it is logged and rejected.
4. **In-camp spend autosave**: Any currency mutation in Hero Camp triggers `PersistStateAsync()` via the Save/Profile in-camp trigger rule.
5. **Atomicity**: A single purchase that costs both gold AND shards must use a confirmed-spend pattern: both deductions succeed, or neither is applied. No partial spends.

### 3.5 Event Bus Messages

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `CurrencyChangedEvent` | Outgoing | `{ gold: long, shards: long, deltaGold: long, deltaShards: long, source: string }` | Published when balance changes. HUD redraws. Source indicates "kill", "completion", or "spend". |
| `EntityDiedEvent` | Incoming | (from Hit Detection → Event Bus) | Consumed to credit gold/shards when the dead entity has a currency drop definition. |

### 3.6 Offline Earnings Credit (handoff to Save/Profile)

Per Save/Profile GDD Section 4 (orphan runstate recovery), offline earnings are credited at app launch:

1. Save/Profile's `RunStateSaveData` contains `goldEarnedThisRun` and `premiumCurrencyEarnedThisRun`.
2. When an orphan `runstate.json` is found, Save/Profile credits those deltas via `ModifyGoldAsync` / `ModifyShardsAsync`.
3. The Currency System treats this as a normal `ModifyXAsync` call — no special handling needed.

### 3.7 Multi-Device Rules

Per Save/Profile:
- Each device reports `earnedThisSession` only — never pushes absolute balance.
- Server calculates authoritative balance as `sum(earnedAcrossAllDevices) - sum(spent)`.
- 15-minute minimum sync interval per device.
- 50,000 gold per 24-hour rolling window cap across all devices.
- Timestamp-based conflict resolution: newest `lastModified` wins (per-field).

The Currency System is agnostic to multi-device complexity — it reports deltas, and Save/Profile handles reconciliation. The Currency System's `GetBalance` always returns the locally-known balance (which may be temporarily out of sync with the server until the next sync round-trip).

---

## 4. Formulas

### 4.1 Gold Per Kill

```
goldPerKill = baseGold + floor(runTimeSeconds × goldTimeScalar) + variance
```

| Variable | Symbol | Type | Default | Range | Description |
|----------|--------|------|---------|-------|-------------|
| baseGold | — | int | tiered (see 4.1a) | 2–50 | Base gold value per enemy tier |
| runTimeSeconds | — | float | 0+ | 0–1800 | Elapsed time since run start |
| goldTimeScalar | — | float | 0.008 | 0.005–0.02 | Gold increase per second survived (~0.5/min) |
| variance | — | int | 0 | -1 to +1 | Small random variance for feel |

#### 4.1a Enemy Tier Base Gold

| Tier | Example | baseGold | Notes |
|------|---------|----------|-------|
| Basic | Ground-level voidspawn | 5 | Every kill, most numerous |
| Fast | Quick skirmisher | 3 | Lower because faster to kill |
| Tank | Armoured corrupted | 12 | Higher, slower to kill |
| Elite | Named miniboss | 50 | Once or twice per run |
| Boss | Zone boss | 200 | Once per run |

### 4.2 Run Completion Gold Bonus

```
completionGold = zoneDepth × GOLD_PER_ZONE + bossDefeated × GOLD_PER_BOSS_KILL + floor(runTimeSeconds × 0.5)
```

| Variable | Symbol | Type | Default | Range |
|----------|--------|------|---------|-------|
| zoneDepth | — | int | — | 1–3 (MVP: 1) |
| GOLD_PER_ZONE | — | int | 200 | 100–500 |
| bossDefeated | — | bool | — | 0 or 1 |
| GOLD_PER_BOSS_KILL | — | int | 500 | 200–1000 |

### 4.3 Per-Run Gold Estimate

For a typical MVP 20-minute run reaching the boss:

- ~200 basic kills × 5 = 1,000
- ~50 fast kills × 3 = 150
- ~10 tank kills × 12 = 120
- 1 elite × 50 = 50
- 1 boss × 200 = 200
- Completion bonus: 1 × 200 + 1 × 500 + 1,200 × 0.5 = 1,300
- Time-scalar bonus: ~200 kills × ~10 extra gold = 2,000 (cumulative over run)

**Total estimate: ~4,820 gold per successful run**
**Typical GPM: ~241** (within 100–500 range, close to default 300)

### 4.4 Aether Shards Per Elite/Boss

```
aetherFromElite = (RNG < ELITE_DROP_CHANCE) ? 1 : 0
aetherFromBoss = 1 + ((RNG < PDR - 1.0) ? 1 : 0)    // PDR default 1.2 → 20% chance of +1
```

| Variable | Symbol | Type | Default | Range | Description |
|----------|--------|------|---------|-------|-------------|
| ELITE_DROP_CHANCE | — | float | 0.33 | 0.25–0.50 | 33% chance of 1 shard per elite kill |
| PDR | premiumDropRate | float | 1.2 | 1.0–1.5 | Variance multiplier (from Save/Profile) |

### 4.5 Per-Run Premium Estimate

For a typical 20-minute run:
- ~2 elite encounters (before boss): 2 × 0.33 = 0.67 average shards
- Boss kill: 1 guaranteed + 0.2 bonus = 1.2 average shards
- Rare drop chance: negligible

**Total estimate: ~1.9 shards per successful run**
**Typical PPH: ~5.7** (above the 1–3 range — may need tuning down. The Save/Profile PPH default of 2 assumes more failed runs in the average.)

### 4.6 GPM / PPH / PDR (for Save/Profile Fraud Detection)

These are **designer-set server constants**, not calculated from player data:

| Constant | Symbol | Default | Range | Purpose |
|----------|--------|---------|-------|---------|
| goldEarnedPerMinuteAvg | GPM | 300 | 100–500 | Fraud cap: max expected gold/min for a normal player |
| premiumPerHourAvg | PPH | 2 | 1–3 | Fraud cap: max expected premium/hour for a normal player |
| premiumDropRate | PDR | 1.2 | 1.0–1.5 | Variance: how "lucky" a drop sequence can be |
| startingGold | — | 0 | 0–500 | Starting gold for new accounts |
| startingPremium | — | 0 | 0–5 | Starting premium for new accounts |

**PPH default of 2 may need revision** based on playtest data. The per-run estimate of ~2 shards per 20 min run yields PPH ~6 for consistent boss-killers. The PPH ceiling is intended for the average player across all runs (including failed ones), so ~2 is a reasonable population average.

**Note to designers**: If playtests show active players consistently earning 6+ PPH, increase the PPH fraud cap accordingly. The fraud check should not false-positive on legitimate high-skill play.

### 4.7 Starting Balances

| Balance | Default | Rationale |
|---------|---------|-----------|
| `startingGold` | 0 | Player earns their first gold during the tutorial run. No free handout. |
| `startingPremium` | 0 | Premium must be earned. First shard comes from the first elite kill. |

---

## 5. Edge Cases

### 5.1 Player Quits Mid-Run Before Any Premium Drop

Gold earned up to the last checkpoint is tracked in `runstate.json`. If the player quits before the first elite kill, `premiumCurrencyEarnedThisRun = 0`. On next launch, the orphan runstate is credited — zero premium, partial gold. No double-credit.

### 5.2 Player Kills Boss But Crashes Before Run Completion Screen

The boss kill fire-and-forgets the gold/shard credit to `CurrencyEarnedThisRun`. Since earnings accumulate during the run (not at completion screen), these are captured in the last auto-saved `runstate.json`. On next launch, orphan detection credits all earnings. **Nothing is lost.**

### 5.3 Multi-Device: Premium Earned on Device A, Gold Earned on Device B

Each device maintains its own `goldEarnedThisRun` and `premiumCurrencyEarnedThisRun`. The server reconciles per-device earnings credits. Per-field `lastModified` timestamps resolve currency conflicts independently — premium has no effect on gold and vice versa.

### 5.4 Spend More Gold Than Available

The Currency System's `CanAfford()` check runs before any spend. If the calling system bypasses the check and calls `ModifyGoldAsync(-cost)` with insufficient balance, the Save/Profile `SaveDataValidator` rejects the mutation (`gold >= 0`). The calling system receives a failure response and must handle accordingly (log error, revert UI state, surface minimal error feedback).

### 5.5 Premium Currency Velocity Fraud Flag

Per Save/Profile: if a single session spends >50% of the player's total lifetime premium earnings (subject to a 1,000-premium floor), the server flags it as fraud and quarantines the payload. The Currency System does not enforce this client-side — the server enforces it during sync. Design intent: prevent a compromised session from wiping a player's premium hoard.

### 5.6 New Player Has Zero Gold

All shop/hub prices should be visible even at zero gold. Affordance (grey, red text) communicates "you need X more gold" rather than hiding the item. This builds anticipation and shows the player what they're working toward.

### 5.7 Server Economy Validation (Alpha — Future State)

When Server Economy Validation (#41) is implemented in Alpha:
- The server validates run duration vs. gold earned ratio.
- The server validates premium earning rate per encounter type.
- Signed telemetry hashes prevent tampering with run results.
- Fraud quarantined payloads are returned with authoritative server snapshot.

---

## 6. Dependencies

### Hard Dependencies (must exist before implementation)

| System | # | Nature of Dependency |
|--------|---|----------------------|
| Save/Profile Persistence | 10 | Persists gold/premiumCurrency balances. Provides `ModifyGoldAsync`, `ModifyShardsAsync`, `CanAfford`, balance reads. Defines fraud detection constants (GPM, PPH, PDR). Handles orphan runstate credit. |
| Network Manager | 7 | Provides sync connection state. System pauses earning writes when Disconnected (queues them for replay). Not strictly required for local-only MVP dev mode. |
| Event Bus | 5 | Consumes `EntityDiedEvent` for currency drops. Publishes `CurrencyChangedEvent` for HUD/camp UI. |

### Soft Dependencies (consume this system)

| System | # | Nature of Dependency |
|--------|---|----------------------|
| Hero Camp Progression | 28 | Reads currency via `GetBalance()`, checks `CanAfford()`, calls `ModifyGoldAsync(-cost)` / `ModifyShardsAsync(-cost)` for upgrades. |
| Run Completion | 36 | Reads `goldEarnedThisRun` / `premiumEarnedThisRun` from run-state. Displays reward summary. Calls final balance credit via Save/Profile. |
| HUD | 30 | Subscribes to `CurrencyChangedEvent` for real-time balance display. |
| Camp Menu UI | 32 | Reads currency for camp screen display. |
| Server Economy Validation | 41 | Alpha — full fraud detection using earning rates, time ratios, signed hashes. |

---

## 7. Tuning Knobs

### Earning Rates

| Knob | Default | Range | Affects | Owner |
|------|---------|-------|---------|-------|
| baseGold (basic) | 5 | 2–10 | Per-kill gold feel | Designer |
| baseGold (fast) | 3 | 1–6 | Per-kill gold for cheap enemies | Designer |
| baseGold (tank) | 12 | 8–20 | Per-kill gold for tough enemies | Designer |
| baseGold (elite) | 50 | 25–100 | Elite kill reward | Designer |
| baseGold (boss) | 200 | 100–500 | Boss kill reward | Designer |
| goldTimeScalar | 0.008 | 0.005–0.02 | Gold growth per second survived | Designer |
| GOLD_PER_ZONE | 200 | 100–500 | Completion bonus per zone depth | Designer |
| GOLD_PER_BOSS_KILL | 500 | 200–1000 | Boss completion bonus | Designer |
| ELITE_DROP_CHANCE | 0.33 | 0.25–0.50 | Premium drop chance per elite | Designer |
| PDR (premiumDropRate) | 1.2 | 1.0–1.5 | Premium variance multiplier | Designer/Server |

### Fraud Detection Constants (server-side)

| Knob | Default | Range | Affects | Owner |
|------|---------|-------|---------|-------|
| GPM | 300 | 100–500 | Max expected gold/min (save fraud cap) | Designer/Server |
| PPH | 2 | 1–3 | Max expected premium/hour (save fraud cap) | Designer/Server |
| startingGold | 0 | 0–500 | New account starting gold | Designer |
| startingPremium | 0 | 0–5 | New account starting premium | Designer |
| Rolling window gold cap (24h) | 50,000 | 10k–500k | Multi-device oscillation cap | Server |

### Premium Sink Costs (design reference for Hero Camp Progression)

| Item | Gold Cost | Shard Cost | Unlock Type |
|------|-----------|------------|-------------|
| Permanent stat upgrade (per tier) | 500–3000 | 0 | Farmable gold sink |
| Basic hero unlock | 2000 | 0 | First hero free / gold-gated |
| Premium hero unlock | 1000 | **10** | Premium showcase |
| Zone unlock (first) | 3000 | 0 | Gold-gated progression |
| Premium zone unlock | 2000 | **15** | Premium gate |
| Signature upgrade (cosmetic/mechanical) | 1500 | **5** | Premium flair |

---

## 8. Acceptance Criteria

### Earning

- **AC1** — **GIVEN** an `EntityDiedEvent` for a basic enemy with no special flags, **WHEN** the Currency System processes it, **THEN** `GetBalance(gold)` increases by `baseGold(basic) + timeScalar` AND no premium is credited.
- **AC2** — **GIVEN** an `EntityDiedEvent` for an elite enemy, **WHEN** the Currency System processes it, **THEN** `GetBalance(gold)` increases by `baseGold(elite)` AND `GetBalance(shards)` increases by 1 with probability `ELITE_DROP_CHANCE` (verified statistically over 1000+ events).
- **AC3** — **GIVEN** an `EntityDiedEvent` for the zone boss, **WHEN** the Currency System processes it, **THEN** `GetBalance(gold)` increases by `baseGold(boss)` AND `GetBalance(shards)` increases by exactly 1 (guaranteed).
- **AC4** — **GIVEN** a run ends with `zoneDepth = 2` and `bossDefeated = true` and `runTimeSeconds = 1200`, **WHEN** the Run Completion system calls the completion credit, **THEN** the total gold credited equals the sum of all per-kill gold + completion formula output.

### Spend

- **AC5** — **GIVEN** `GetBalance(gold) = 1000`, **WHEN** `CanAfford(goldCost = 500, shardCost = 0)`, **THEN** returns `true`.
- **AC6** — **GIVEN** `GetBalance(gold) = 200`, **WHEN** `CanAfford(goldCost = 500, shardCost = 0)`, **THEN** returns `false`.
- **AC7** — **GIVEN** `GetBalance(gold) = 1000` AND `GetBalance(shards) = 5`, **WHEN** the Hero Camp Progression system calls `ModifyGoldAsync(-1200)` AND `ModifyShardsAsync(-3)`, **THEN** the gold mutation is **REJECTED** (SaveDataValidator blocks negative gold) AND `GetBalance(shards)` remains 5 (no partial spend — atomicity preserved).

### Persistence Handoff

- **AC8** — **GIVEN** a run in progress with `goldEarnedThisRun = 500` and `premiumEarnedThisRun = 2`, **WHEN** Save/Profile reads the run state for autosave, **THEN** `RunStateSaveData.goldEarnedThisRun = 500` AND `RunStateSaveData.premiumCurrencyEarnedThisRun = 2`.
- **AC9** — **GIVEN** `ModifyGoldAsync(500)` is called mid-run, **WHEN** the value is persisted via Save/Profile, **THEN** `persistent.json.gold` equals the pre-call balance + 500 AND `goldLastModified` is updated to the current timestamp.

### Multi-Device

- **AC10** — **GIVEN** the same account logs in on Device A (earns 300 gold) and Device B (earns 200 gold), **WHEN** both sync, **THEN** the server-authoritative balance equals `preStartBalance + 500` AND each device's local balance eventually converges to the server value.

### Edge Cases

- **AC11** — **GIVEN** a crash occurs mid-run after earning 100 gold and 1 aether shard, **WHEN** the app relaunches and orphan runstate recovery runs, **THEN** `GetBalance(gold)` includes the 100 AND `GetBalance(shards)` includes the 1 (no double-credit).
- **AC12** — **GIVEN** `CanAfford(goldCost = 999999, shardCost = 0)` when `GetBalance(gold) = 100`, **WHEN** called, **THEN** returns `false` AND the HUD shows the item as unaffordable (greyed with price in red).

### Performance

- **AC13** — **GIVEN** 200 basic enemies die within 5 seconds (late-game wave), **WHEN** the Currency System processes 200 `EntityDiedEvent` messages, **THEN** all 200 gold credits are applied AND total processing time is under 16ms (single frame budget).
