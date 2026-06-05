# Story 001: Damage & Health Core

- **Epic**: Damage & Health
- **System**: Damage & Health — Core
- **Type**: Integration
- **Priority**: P1
- **Estimate**: 4h
- **Status**: Complete
- **Last Updated**: 2026-06-04

## Completion Notes
**Completed**: 2026-06-04
**Criteria**: 5/5 passing
**Deviations**:
- ADVISORY: `HitEvent` extended with `DamageValue` — not listed in ADR-002 event catalogue. Minor, pragmatic for pipeline.
- ADVISORY: Faction gate in HitResolver (upstream) rather than DamageApplicationService.
**Test Evidence**: Logic: test files at `Assets/_TinyRift/Tests/EditMode/Combat/HealthComponentTests.cs` and `Assets/_TinyRift/Tests/EditMode/Combat/DamageApplicationServiceTests.cs`
**Code Review**: Complete (APPROVED WITH SUGGESTIONS)

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-dmghealth-001` | HealthComponent with max/current HP + TakeDamage damage calc | ✅ ADR-001 |
| `TR-dmghealth-003` | EntityDied published when HP ≤ 0 | ✅ ADR-002 |
| `TR-dmghealth-001` | Faction gate — same-faction hits ignored via HitDetectionRegistry | ✅ ADR-002 |
| `TR-dmghealth-001` | Heal(int amount) clamps to MaxHP | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `IDamageApplicationService` registered as interface singleton in TinyRiftScope
- `IHealth` components resolved individually per entity (not singleton)

**ADR-002 (Event Bus Contract):**
- Subscribes to `HitEvent` — consumes hitbox/hurtbox collision data
- Publishes `DamageAppliedEvent` (amount, source, target, isDead)
- Publishes `EntityDiedEvent` (entity, source, position)

**Control Manifest (Feature Layer):**
- Feature layer has no ADRs yet written (`docs/architecture/control-manifest.md:174`)
- Follow Foundation-layer naming conventions (PascalCase classes, `_camelCase` fields)

## Description

Implements the core damage pipeline: `HitEvent` → faction check → `HealthComponent.TakeDamage()` → `DamageAppliedEvent` → `EntityDiedEvent` on death. Provides `IHealth` interface for entities to expose HP, and `IDamageApplicationService` as the orchestrator that bridges hit detection to health.

## Design

```csharp
public interface IHealth
{
    int MaxHP { get; }
    int CurrentHP { get; }
    float HPRatio { get; }
    bool IsAlive { get; }
    event Action<DamageAppliedArgs> OnDamageTaken;
    event Action<EntityDiedArgs> OnDeath;

    DamageResult TakeDamage(DamageArgs args);
    void Heal(int amount);
    void Kill(GameObject source);
}

public interface IDamageApplicationService
{
    void ApplyHit(HitEvent hitEvent);
}
```

### Damage Pipeline

1. `HitEvent` arrives on Event Bus (from HD-002)
2. `DamageApplicationService` resolves source damage value (from `IHitbox.DamageValue`)
3. Faction check via `HitDetectionRegistry.IsValidCollision(attacker, defender)`
4. If invalid (same faction), discard silently
5. If valid, call `IHealth.TakeDamage()` on defender
6. Publish `DamageAppliedEvent`
7. If defender HP ≤ 0, publish `EntityDiedEvent`

### HealthComponent

- MonoBehaviour implementing `IHealth`
- `MaxHP` set via `[SerializeField] int maxHp = 100`
- `CurrentHP` initialized to MaxHP on Awake
- `TakeDamage` clamps to 0, fires events
- `Heal` clamps to MaxHP
- `Kill` sets HP to 0 and fires death event

## Acceptance Criteria

1. **GIVEN** an entity with IHealth (HP 100), **WHEN** HitEvent arrives with damage 30 from enemy faction, **THEN** HP becomes 70, DamageAppliedEvent published with amount=30
2. **GIVEN** an entity with IHealth (HP 10), **WHEN** HitEvent arrives with damage 20, **THEN** HP becomes 0, EntityDiedEvent published
3. **GIVEN** a same-faction hit (Player hitbox → Player hurtbox), **WHEN** HitEvent arrives, **THEN** no damage applied, no events published
4. **GIVEN** an entity with IHealth (HP 80), **WHEN** Heal(30) called, **THEN** HP becomes 100 (clamped)
5. **GIVEN** a dead entity (HP 0), **WHEN** TakeDamage called again, **THEN** no further damage applied, no death event republished

## QA Test Cases

- **AC1 (TakeDamage)**: Create entity with IHealth (HP 100). Dispatch HitEvent with damage 30 from enemy faction. Verify HP=70, DamageAppliedEvent(amount=30) published.
- **AC2 (Death)**: Entity with HP 10. Dispatch HitEvent with damage 20. Verify HP=0, EntityDiedEvent published.
- **AC3 (No friendly fire)**: Same-faction HitEvent. Verify no HP change, no events published.
- **AC4 (Heal clamp)**: Entity HP 80. Heal(30). Verify HP=100 (clamped to MaxHP).
- **AC5 (Dead no-op)**: Entity HP 0. Dispatch another HitEvent. Verify no HP change, no death event republished.

**Edge cases**: Zero damage hit, overflow damage (>MaxHP remaining), heal on dead entity (no-op).

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/Combat/DamageApplicationServiceTests.cs`
- `Assets/_TinyRift/Tests/EditMode/Combat/HealthComponentTests.cs`

## Out of Scope
- Status effect application (deferred to Status Effect System)
- Invincibility frames (separate story)
- Damage formula with mitigation/defense (flat subtraction for MVP)
- Heal-over-time or regen effects

## Dependencies

- **Depends on**: HD-002 (Hit Detection & Event Dispatch) — consumes HitEvent
- **Depends on**: HitDetectionRegistry — faction check
- **Unlocks**: HUD health bar, Enemy death handling, VFX on damage

## Risks

- **PERF**: Damage pipeline must resolve in < 0.05ms per HitEvent — no heap allocations per TakeDamage call. Dictionary lookups by EntityId are acceptable.
- **LOW**: Multiple HitEvents in same frame — HealthComponent must be thread-safe or main-thread only
- **LOW**: Entity dies during HitEvent processing loop — guard with IsAlive check at entry
