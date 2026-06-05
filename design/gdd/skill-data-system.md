# Skill Data System

> **Status**: Drafted (awaiting design review)
> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS (accepted 2026-05-26 — added `LoreFragmentKey`/`ZoneAffinityKey` to schema, `SynergyOverrideKey` to UpgradeTier)
> **Author**: game-designer + technical-director
> **Last Updated**: 2026-05-26
> **Implements Pillar**: P2 (Emergent Build-Crafting) — skill data is the atomic unit of build-crafting; all draft choices and synergy rules operate on skill instances
> **Constraint**: C3 — pure data references (IDs/keys/enums) only. Never runtime types from higher layers.

## Overview

The Skill Data System is the data configuration layer that defines every skill in the game — its identity, mechanics, progression, and presentation. Each skill is a ScriptableObject asset containing a unique ID, element type, rarity tier, cooldown, damage parameters, orbit/burst behavior flags, upgrade definitions, VFX profile references, and audio cue keys. Skills are authored by designers as assets, referenced by ID throughout the codebase, and never instantiated as runtime types from higher layers (C3 constraint). Without this system, the 11 downstream dependents (combat, drafting, HUD, save, VFX, audio) would have no shared vocabulary for what a skill is — each system would define its own skill shape, producing data fragmentation and integration bugs.

## Player Fantasy

The player feels the Skill Data System as the **palette of possibility** in every draft choice. Each rune card in the draft panel represents a skill definition — its element icon, rarity glow, damage preview, and cooldown bar all read from the same data source. When a skill upgrades (orbit damage +50%, ice burst gains freeze chance), the upgrade path is defined in the skill's ScriptableObject, not hard-coded in a combat script. The fantasy is one of **tactile discovery**: every rune you pick has weight, identity, and a growth trajectory you can feel as the run progresses. The system is invisible but the variety it enables — 5-6 distinct skills, each with 3 upgrade tiers and distinct VFX profiles — is what makes each run's build feel like your own.

## Detailed Design

### Core Rules

1. Every skill in the game is defined by a single `SkillDefinition` ScriptableObject asset. These are the authoritative data source for all skill properties.
2. `SkillDefinition` contains only pure data: enums, strings, floats, ints, and structs. It never references MonoBehaviours, GameObjects, Components, or any gameplay-layer type.
3. Cross-system references (VFX, audio, icons, projectiles) use **string keys** — the owning system resolves the key to an asset at runtime. This maintains the C3 boundary: Skill Data does not depend on VFX/Audio/Gameplay layers.
4. Skill identity is a `string SkillId` in the format `"skill_<element>_<name>"`. This ID is the stable reference used by all downstream systems, serialization, and network sync.
5. Skills are organized by `SkillType` (Orbit or Burst) and `ElementType`. Each skill type has dedicated fields on the definition; unused fields are null/zero.
6. Upgrades are defined inline as a `SkillUpgradeTier[3]` array on the definition — not as separate assets. Each tier describes deltas (damage multiplier, cooldown multiplier, additional projectiles, etc.).
7. Rarity (Common/Uncommon/Rare) is a fixed property of each `SkillDefinition`. Multipliers are stored per-definition (not a global table) to allow individual tuning.
8. `SkillInstance` is the runtime representation of a drafted skill. It stores: the owning `SkillDefinition` reference, current upgrade tier, cooldown timer, and orbit angle. It never holds Unity Object references (C3 compliant).
9. All `SkillDefinition` assets are registered in a `SkillDatabase` ScriptableObject singleton. Downstream systems access definitions through `SkillDatabase.GetById(string id)`.
10. MVP scope: 5-6 standalone skills (Fire/Ice/Lightning, mix of Orbit and Burst). No synergy data. Synergy rules are deferred to the Synergy System (Alpha tier).

### Skill Definition Schema

**Identity:**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `SkillId` | `string` | `"skill_fire_orb"` | All systems (identity reference) |
| `SkillNameKey` | `string` | `"skill_fire_orb_name"` | HUD, Draft Panel UI (localization key) |
| `SkillType` | `SkillType` | `SkillType.Orbit` | Orbit Combat, Burst Skill (routes to correct system) |
| `ElementType` | `ElementType` | `ElementType.Fire` | Status Effect, VFX, Audio, Draft Panel |
| `Rarity` | `Rarity` | `Rarity.Common` | Rune Draft, Draft Panel UI |

**Mechanics (shared):**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `BaseDamage` | `float` | `15.0` | Damage & Health, Orbit/Burst Combat |
| `CooldownSeconds` | `float` | `5.0` | Burst Skill (orbit skills ignore this) |
| `DamageTypeFlags` | `DamageTypeFlags` | `Projectile` | Damage & Health |

**Mechanics (Orbit-specific):**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `OrbitSpeed` | `float` | `120.0` (deg/sec) | Orbit Combat |
| `OrbitRadius` | `float` | `3.5` | Orbit Combat |
| `ProjectileCount` | `int` | `3` | Orbit Combat |
| `TargetPriority` | `TargetPriority` | `TargetPriority.Nearest` | Orbit Combat |
| `ProjectileKey` | `string` | `"proj_fire_orb"` | Combat systems → resolved via ProjectileRegistry |

**Mechanics (Burst-specific):**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `CastRange` | `float` | `8.0` | Burst Skill |
| `AoeRadius` | `float` | `2.5` | Burst Skill (0 = single target) |
| `AimAngle` | `float` | `45.0` | Burst Skill (cone width; 360 = omni) |
| `ProjectileKey` | `string` | `"proj_ice_shard"` | Burst Skill |

**Upgrades:**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `UpgradeTiers` | `SkillUpgradeTier[3]` | See Upgrade table | Rune Draft, Combat systems |

**Narrative (deferred — nullable, zero for MVP):**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `LoreFragmentKey` | `string` | `"lore_fire_archmage_warning"` | Lore Fragment System (future — narrative power track per P1) |
| `ZoneAffinityKey` | `string` | `"zone_amber_caverns"` | Zone Definition / World State (future — zone-specific bonus per P1) |

**Presentation:**
| Field | Type | Example | Consumer |
|-------|------|---------|----------|
| `IconKey` | `string` | `"icon_skill_fire_orb"` | HUD, Draft Panel UI |
| `ElementColor` | `Color` | `#FF4500` | HUD, Draft Panel UI (element identity color) |
| `VfxProfileKey` | `string` | `"vfx_fire_orb_cast"` | SkillPresentationAdapter → VFX System |
| `HitVfxKey` | `string` | `"vfx_fire_orb_impact"` | SkillPresentationAdapter → VFX System |
| `AudioCueKey` | `string` | `"sfx_fire_orb_launch"` | SkillPresentationAdapter → Audio System |
| `HitAudioCueKey` | `string` | `"sfx_fire_orb_hit"` | SkillPresentationAdapter → Audio System |
| `PresentationProfileKey` | `string` | `"pres_fire_projectile"` | SkillPresentationAdapter (timing data) |

**Supporting enums:**
```csharp
public enum SkillType { Orbit, Burst }

public enum ElementType { None = 0, Fire, Ice, Lightning }

public enum Rarity { Common, Uncommon, Rare }

public enum TargetPriority { Nearest, LowestHp, Random }

[Flags]
public enum DamageTypeFlags
{
    None = 0,
    Projectile = 1 << 0,
    Melee = 1 << 1,
    Aoe = 1 << 2,
    Dot = 1 << 3
}
```

**SkillUpgradeTier struct:**
```csharp
[System.Serializable]
public struct SkillUpgradeTier
{
    public int TierLevel;                     // 1, 2, 3
    public string UpgradeNameKey;             // Localization key
    public string UpgradeDescriptionKey;      // "Fires 2 additional projectiles"
    public float DamageMultiplier;            // Applied to BaseDamage at this tier
    public float CooldownMultiplier;          // Applied to CooldownSeconds
    public int AdditionalProjectiles;         // Orbit count or burst projectiles
    public float AdditionalAoeRadius;         // Burst AoE bonus
    public float AdditionalOrbitSpeed;        // Orbit rotation speed bonus
    public string UpgradeVfxKey;              // Optional: VFX that changes at this tier
    public string SynergyOverrideKey;         // Optional — if set, this upgrade tier grants/reveals a synergy instead of numeric stats. Null for MVP. Forward extension point for Alpha synergy system.
}
```

### Skill Instance vs Skill Definition

```csharp
// SkillDefinition — static data asset (ScriptableObject). Data layer.
public class SkillDefinition : ScriptableObject { /* fields from schema above */ }

// SkillInstance — runtime state. Data layer (no Unity Object refs).
public struct SkillInstance
{
    public SkillDefinition Definition;        // Reference to static data
    public int CurrentTier;                   // 0-2 (current upgrade tier)
    public float CooldownTimer;               // Seconds remaining
    public float OrbitCurrentAngle;           // Orbit-only: current orbital position
    public bool IsActive;                     // Whether the skill is currently active
}

// SkillRegistry — VContainer singleton. Bridges ID → Definition lookup.
public class SkillRegistry
{
    private readonly Dictionary<string, SkillDefinition> _definitions;

    public SkillDefinition GetDefinition(string skillId) { /* lookup */ }
    public SkillInstance CreateInstance(string skillId) { /* new SkillInstance with tier=0 */ }
    public SkillInstance UpgradeInstance(SkillInstance instance) { /* bump tier */ }
}
```

| Aspect | SkillDefinition | SkillInstance |
|--------|-----------------|---------------|
| Lifetime | Project lifetime | Per run |
| Storage | ScriptableObject asset | Runtime memory (struct) |
| Mutability | Immutable (authoring only) | Mutable (cooldown, tier) |
| Unity Object refs | None (C3 compliant) | None (C3 compliant) |
| Serialization | Asset GUID | `SkillId` string (for save) |
| Who owns | Designer (via asset) | Build State system |

### Skill Registry

The `SkillRegistry` is a VContainer singleton registered in `TinyRiftScope`. It:

1. Loads all `SkillDefinition` assets via the `SkillDatabase` ScriptableObject at startup.
2. Exposes `GetDefinition(string skillId)` — returns the definition or logs error + returns null.
3. Exposes `CreateInstance(string skillId)` — creates a `SkillInstance` at tier 0.
4. Exposes `UpgradeInstance(SkillInstance instance)` — returns a new `SkillInstance` with `CurrentTier++`.
5. Validates all IDs on load (logs warnings for duplicates or missing icons/keys).
6. Provides `GetAllSkillIds()` for the Rune Draft system to build its draft pool.

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| Orbit Combat | Reads `SkillDefinition` via `SkillRegistry.GetDefinition(id)` | OrbitCombat → SkillData | `SkillType.Orbit` skills → orbit speed, radius, count, projectile key, base damage |
| Burst Skill | Reads `SkillDefinition` via `SkillRegistry.GetDefinition(id)` | BurstSkill → SkillData | `SkillType.Burst` skills → cooldown, range, AoE, aim angle, projectile key, base damage |
| Damage & Health | Reads `BaseDamage`, `ElementType`, `DamageTypeFlags` from `SkillRegistry` | DmgHealth → SkillData | Damage calculation params |
| Status Effect | Reads `ElementType` → maps to status type via own mapping table | StatusFX → SkillData | Element → Burn/Freeze/Stun |
| Rune Draft | Reads all available `SkillDefinition` assets, upgrade tiers at `CurrentTier+1` | RuneDraft → SkillData | Skill names, icons, rarity weights, upgrade descriptions |
| Build State | Stores `SkillId` strings + tier levels for per-run loadout | BuildState → SkillData | Serialized `DraftedSkillData` structs (ID + tier) |
| HUD | Reads `SkillId`, `IconKey`, `ElementColor`, `CooldownSeconds` | HUD → SkillData | Skill slot display |
| Draft Panel UI | Reads `SkillNameKey`, `IconKey`, `Rarity`, `ElementType`, upgrade descriptions | DraftUI → SkillData | Draft card content |
| SkillPresentationAdapter | Reads `VfxProfileKey`, `HitVfxKey`, `AudioCueKey`, `HitAudioCueKey`, `PresentationProfileKey` | Adapter → SkillData | Presentation routing keys |
| Save/Profile | Reads/Saves `SkillId` strings for persistent unlock data | Save → SkillData | Unlock state serialization |
| Synergy System (deferred) | Reads `ElementType` for compound reaction rules | Synergy → SkillData | Element combination mapping |
| Event Bus | Skill data is referenced by `SkillId` in event payloads (never passed as objects) | SkillData → Event | ID references only, per C3 |
| SkillDatabase | All `SkillDefinition` assets registered here; downstream goes through `SkillRegistry` | SkillData → DB | Centralized lookup

## Formulas

None. The Skill Data System defines data fields (damage, cooldown, multipliers) but performs no calculations. All formulas that consume these values live in the systems that use them:
- **Damage calculation**: Owned by Damage & Health System. Reads `BaseDamage` × `UpgradeTier.DamageMultiplier` × `Rarity` modifiers.
- **Cooldown**: Owned by Burst Skill System. Reads `CooldownSeconds` × `UpgradeTier.CooldownMultiplier`.
- **Draft probability**: Owned by Rune Draft System. Uses `Rarity` for weight calculations.

The Skill Data System is a data provider, not a computation engine.

## Edge Cases

- **If `SkillRegistry.GetDefinition(id)` is called with an ID that doesn't exist**: Returns `null`. Caller must handle null gracefully (log error, skip the skill, or show a placeholder). This typically means save data references a skill that was removed — the save should be repaired or the skill entry skipped.
- **If a `SkillDefinition` asset is missing from the `SkillDatabase`** (rename/move corrupted the reference): The database's `OnValidate()` or startup validation logs the missing entry. The skill is simply unavailable — no crash. Draft pool excludes any skills with null definitions.
- **If `UpgradeInstance()` is called on a `SkillInstance` at `CurrentTier = 2`** (max tier): No-op. Returns the same instance. The Rune Draft system should not present upgrade choices for max-tier skills.
- **If two `SkillDefinition` assets share the same `SkillId`**: The `SkillDatabase` startup validation logs a duplicate error. The last one loaded wins. This is a data authoring error — the designer must fix it.
- **If `BaseDamage` is 0 or negative**: The skill compiles and can be drafted, but deals no damage. `OnValidate()` logs a warning. This is a data authoring oversight.
- **If string keys are empty** (`VfxProfileKey = ""`, `AudioCueKey = ""`): The downstream system resolves the empty key as "no effect" — no VFX plays, no sound. `OnValidate()` logs a warning.
- **If `SkillInstance` is created with an invalid `SkillId`**: `CreateInstance()` returns a default `SkillInstance` with `Definition = null`. The caller null-checks `Definition` before using it. Systems that receive null-definition instances should log the error and skip processing.
- **If save data references a skill that no longer exists** (skill removed from game): On load, `BuildState.Deserialize()` skips unknown `SkillId` entries. A warning is logged. The player's build is still valid — the missing skill is simply absent.
- **If the same skill is drafted twice** (should not happen, but possible via bug): The Rune Draft system should check `BuildState.HasSkill(id)` before presenting choices. If a duplicate is somehow created, the `SkillInstance` carries its own state — two instances with the same definition are independent.

## Dependencies

**Upstream (this system depends on these)**: None. Skill Data System is a Foundation-layer system with zero upstream dependencies. `SkillDefinition` assets are authored directly as ScriptableObjects and require only the Unity serialization layer.

**Downstream (systems that depend on this one)**:

| System | Type | Interface |
|--------|------|-----------|
| Orbit Combat | Hard | Reads `SkillDefinition` fields for Orbit-type skills |
| Burst Skill | Hard | Reads `SkillDefinition` fields for Burst-type skills |
| Damage & Health | Hard | Reads `BaseDamage`, `ElementType`, `DamageTypeFlags` |
| Status Effect | Soft | Reads `ElementType` (maps to status via own table) |
| Rune Draft | Hard | Reads all skills for draft pool, upgrade tiers for upgrade choices |
| Build State | Hard | Stores `SkillId` + tier for per-run loadout |
| HUD | Hard | Reads skill identity, icon, cooldown for skill slot display |
| Draft Panel UI | Hard | Reads skill name, icon, rarity for draft card content |
| SkillPresentationAdapter | Hard | Reads VFX/audio/presentation keys for animation routing |
| Save/Profile | Soft | Serializes `SkillId` strings for persistent unlock data |
| Synergy System (Alpha) | Hard (deferred) | Reads `ElementType` for reaction rules |

*Hard = system cannot function without this. Soft = enhanced by this but works without it.*

## Tuning Knobs

The Skill Data System has no system-level tuning knobs. All tunable values (damage, cooldown, orbit speed, etc.) are fields on individual `SkillDefinition` assets — they are per-skill tuning, not system-level knobs. The maximum upgrade tier (3) is a hard-coded design decision; changing it would require modifying the `SkillUpgradeTier[3]` array size.

Systems that consume skill data have their own tuning knobs for how they interpret the data (e.g., Damage & Health's damage cap, Rune Draft's rarity weight table).

## Visual/Audio Requirements

The Skill Data System itself has no visual or audio output. It provides the data keys that drive presentation in other systems:

| Data Field | Used By | To Produce |
|-----------|---------|------------|
| `ElementColor` | HUD, Draft Panel UI | Element-specific tint on skill icons, borders, and cooldown sweeps (art bible Section 8.2: fire=red/orange, ice=cyan/white, lightning=purple/yellow) |
| `IconKey` | HUD, Draft Panel UI | Skill icon sprite (48×48 rune glyph per art bible Section 6.4) |
| `VfxProfileKey` | SkillPresentationAdapter → VFX System | Cast VFX (elemental swirl, rune ignition per art bible Section 8.5.1) |
| `HitVfxKey` | SkillPresentationAdapter → VFX System | Impact VFX (element burst, shatter per Section 8.5.2) |
| `AudioCueKey` | SkillPresentationAdapter → Audio System | Cast SFX (fire whoosh, ice shatter, lightning crack) |
| `HitAudioCueKey` | SkillPresentationAdapter → Audio System | Hit SFX (impact thud per element) |
| `PresentationProfileKey` | SkillPresentationAdapter | Animation timing data (cast wind-up, projectile speed, hit-stop, screen shake — mapped to specific PresentationProfile assets) |

The owning systems resolve string keys to runtime assets via their own registries (VfxLibrary, AudioLibrary, PresentationProfileRegistry). The Skill Data System never holds or resolves these references directly.

> 📌 **Asset Spec** — Visual/Audio requirements are defined. After the art bible is approved, run `/asset-spec system:skill-data-system` to produce per-asset visual descriptions, dimensions, and generation prompts from this section.

## UI Requirements

The Skill Data System has no direct UI. It provides data that UI systems display:
- **HUD**: Reads `IconKey` (sprite), `ElementColor` (tint), `CooldownSeconds` (cooldown sweep animation), `SkillNameKey` (tooltip label) for each active skill slot
- **Draft Panel UI**: Reads `SkillNameKey`, `IconKey`, `Rarity` (border glow tier), `ElementType` (element icon header), `UpgradeTiers[currentTier]` (upgrade description text for upgrade choices; tier 0 stats for new skill choices)
- **Codex (future)**: Reads `SkillId`, `SkillNameKey`, `ElementType` for lore/skill reference display

No per-data UI is owned by the Skill Data System itself.

## Open Questions

| Question | Options | Impact | Target Resolution |
|----------|---------|--------|-------------------|
| Should `SkillDefinition` use inheritance (`OrbitSkillDefinition`/`BurstSkillDefinition`) or flat + component data? | Inheritance (cleaner, separate assets per type) vs. Component (single asset, nullable structs for Orbit/Burst fields) | Inheritance: clearer editor UX for 5-6 skills. Component: simpler code, no AOT stripping risk for derived types. | During implementation — start with inheritance, fall back to component if stripping issues arise |
| Should rarity multipliers be per-definition or global? | Per-definition (each skill has its own `rarityDamageMultiplier`) vs. Global table (Rarity→multiplier map) | Per-def: maximum tuning flexibility. Global: enforces consistency, easier to rebalance | During Rune Draft System GDD — global table recommended for MVP consistency |
| Should `SkillInstance` be a struct or a class? | Struct (value type, no heap alloc) vs Class (reference type, mutable, easier to track) | Struct: better perf, but must be passed by ref or copied. Class: GC allocation per skill per run | During implementation — struct for perf, passed by ref where mutated |
| Should `PresentationProfile` be split per skill or shared per skill type? | Per-skill (each skill has independent timing) vs. Per-type (all orbit skills share one profile) vs. Hybrid | Per-skill: maximum animation variety. Per-type: simpler, 1 profile for MVP. Hybrid: shared base, per-skill overrides | During SkillPresentationAdapter GDD — shared per-type for MVP, hybrid when adding more skills |

## Acceptance Criteria

- **GIVEN** a `SkillDefinition` asset with valid fields, **WHEN** it is referenced by `SkillRegistry.GetDefinition(id)`, **THEN** the returned definition contains all authored fields (damage, cooldown, element, icons, keys) exactly as defined.
- **GIVEN** a `SkillDatabase` with 5 skill definitions, **WHEN** `SkillDatabase.GetAllSkillIds()` is called, **THEN** it returns exactly 5 unique string IDs.
- **GIVEN** two `SkillDefinition` assets with the same `SkillId`, **WHEN** the `SkillDatabase` loads, **THEN** a duplicate ID warning is logged and the last-loaded definition wins.
- **GIVEN** a valid `SkillId`, **WHEN** `SkillRegistry.CreateInstance(id)` is called, **THEN** a `SkillInstance` is returned with `Definition` matching the requested ID, `CurrentTier = 0`, and `CooldownTimer = 0`.
- **GIVEN** a `SkillInstance` at tier 0, **WHEN** `SkillRegistry.UpgradeInstance(instance)` is called, **THEN** a new `SkillInstance` is returned with `CurrentTier = 1`.
- **GIVEN** a `SkillInstance` at tier 2 (max), **WHEN** `SkillRegistry.UpgradeInstance(instance)` is called, **THEN** the same instance is returned (no-op).
- **GIVEN** an invalid `SkillId` that does not exist in the database, **WHEN** `SkillRegistry.GetDefinition(id)` is called, **THEN** it returns `null`.
- **GIVEN** a `SkillDefinition` with `BaseDamage = 0`, **WHEN** the definition is loaded, **THEN** `OnValidate()` logs a warning but the asset is not rejected.
- **GIVEN** a `SkillDefinition` with a valid `SkillId`, **WHEN** its `SkillType` is `Orbit`, **THEN** the Orbit-specific fields (`OrbitSpeed`, `OrbitRadius`, `ProjectileCount`) have non-zero values and Burst-specific fields (`CastRange`, `AoeRadius`) are zero.
- **GIVEN** a `SkillDefinition` with a valid `SkillId`, **WHEN** its `SkillType` is `Burst`, **THEN** the Burst-specific fields (`CooldownSeconds`, `CastRange`, `AimAngle`) have non-zero values and Orbit-specific fields (`OrbitSpeed`, `OrbitRadius`) are zero.
- **GIVEN** a `SkillInstance` struct, **WHEN** it is serialized to JSON via `JsonUtility`, **THEN** the JSON contains `skillDefinitionId` (string) and `currentTier` (int) but no Unity Object references.
- **GIVEN** a `SkillDefinition` authored in the Editor, **WHEN** inspected in the Inspector, **THEN** all string keys (`VfxProfileKey`, `AudioCueKey`, `IconKey`, `ProjectileKey`, `PresentationProfileKey`) are editable text fields, not object pickers (ensures C3 compliance — no direct asset references to higher-layer prefabs).
