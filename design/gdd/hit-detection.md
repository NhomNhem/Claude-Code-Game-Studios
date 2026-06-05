# Hit Detection

> **Status**: Designed (pending review)
> **Author**: user + agents
> **Last Updated**: 2026-05-26
> **Implements Pillar**: Pillar 3 — Snappy 20–30 Minute Sessions (responsive combat feel)

## Overview

Hit Detection manages collision hitbox/hurtbox pairing between player projectiles and enemies, and between enemies and the player. It wraps the template's existing 3D trigger-based hit detection (`DamageEntity.OnTriggerEnter`, `MonsterEntity.OnTriggerEnter`) with a faction-aware registration system and outputs hit events to the Event Bus. It does NOT replace the template's collision detection — it extends it with structured routing and cross-system event dispatch.

## Player Fantasy

The player feels hits land cleanly: every projectile that visually connects also registers damage, there is no "that should have hit" desync, and hits feel weighty because they trigger VFX, audio, and hit-stop through the Event Bus. The hit detection itself is invisible — players only feel its absence when it goes wrong.

## Detailed Design

### Core Rules

1. **Faction system** — `Hitbox` and `Hurtbox` MonoBehaviours each declare a `Faction` (Player/Enemy/Neutral). Hits only resolve when `hitbox.Faction != hurtbox.Faction`.
2. **Registration** — GameObjects register their hitboxes and hurtboxes on `Start()` via `HitDetectionRegistry.Register(hitbox)` and `Register(hurtbox)`. Unregister on `OnDestroy()`.
3. **Event dispatch** — When a valid hit is detected, publishes a `HitEvent` struct to the Event Bus containing: attacker, target, damage value, element type, hit position, hit normal.
4. **Per-target cooldown** — A `Dictionary<Collider, float>` enforces a 0.3s minimum between consecutive hits on the same target (matches template's existing cooldown). Configurable via tuning knob.
5. **Template wrapping** — Our `HitDetectionManager` observes `DamageEntity.OnTriggerEnter` via a bridge component (no vendor code modification). The bridge reads the collision, builds the `HitEvent`, and passes it to the Event Bus. Template's existing damage application continues to work — our layer is additive.
6. **No overlap queries** — All detection is event-driven via Unity's trigger system. No manual `Physics.OverlapSphere` or raycast sweeps. This matches template patterns.
7. **Hit event is fire-and-forget** — The Event Bus consumer (Damage & Health System) owns damage calculation. Hit Detection only routes the collision event — it does not apply damage.

### Faction Rules

| Hitbox Faction | Hurtbox Faction | Result |
|---------------|-----------------|--------|
| Player | Enemy | Hit — publish event |
| Enemy | Player | Hit — publish event |
| Player | Player | Ignored (no friendly fire) |
| Enemy | Enemy | Ignored unless Neutral |
| Neutral | Any | Hit |

### API Surface

```csharp
public struct HitEvent
{
    public GameObject Attacker;
    public GameObject Target;
    public Vector3 HitPoint;
    public Vector3 HitNormal;
    public ElementType Element;       // fire, ice, lightning, void, physical
    public float BaseDamage;          // from skill data, before modifiers
}

public class HitDetectionRegistry : MonoBehaviour
{
    public static void Register(IHitBox hitbox);
    public static void Unregister(IHitBox hitbox);
    public static void Clear();                     // scene transition
}

public interface IHitBox
{
    Faction Faction { get; }
    Collider Collider { get; }
}
```

### Interactions with Other Systems

| System | Interface | Direction | Data |
|--------|-----------|-----------|------|
| Event Bus | Publishes `HitEvent` | HitDetect → Bus | HitEvent struct |
| Damage & Health | Consumes `HitEvent` for damage calc | Bus → DmgHealth | HitEvent with element + base damage |
| VFX System | Consumes `HitEvent` for impact VFX | Bus → VFX | Hit position, element type |
| Audio System | Consumes `HitEvent` for hit SFX | Bus → Audio | Element type, hit position |
| Screen Shake | Consumes `HitEvent` for shake | Bus → Shake | Hit element (element determines shake profile) |
| SkillPresentationAdapter | Consumes `HitEvent` for hit-stop | Bus → Adapter | Hit event timing |

## Formulas

None. Hit Detection routes collision events. Damage calculation is owned by Damage & Health System.

## Edge Cases

- **If a projectile hits two enemies in the same frame** (piercing shot): `OnTriggerEnter` fires for each enemy independently. Both `HitEvent`s are published. Damage & Health handles each separately.
- **If a projectile hits the same enemy twice within 0.3s**: Per-target cooldown suppresses the second hit. No event is published.
- **If a hitbox is destroyed mid-collision** (enemy dies during hit): `Hitbox.OnDestroy()` unregisters it. In-flight `OnTriggerEnter` callbacks complete normally — the `GameObject` is still valid during the current frame.
- **If a hurtbox has no corresponding `MonsterHealth` or `CharacterEntity`**: The HitEvent is still published. Damage & Health checks for the component and silently ignores if absent.
- **If two hitboxes overlap simultaneously** (AoE explosion): Each hitbox independently triggers `OnTriggerEnter`. Events publish per-hitbox, not batched.
- **If a hitbox and hurtbox share the same Faction** (player projectile hits player): Evaluated but suppressed. No event published.

## Dependencies

| System | Dependency | Direction | Notes |
|--------|-----------|-----------|-------|
| Event Bus | Required | HitDetect → Bus | Publishes HitEvent |
| Unity Physics (3D triggers) | Required | HitDetect → Engine | OnTriggerEnter/Stay events |
| VContainer | Required | Scope → HitDetect | Registration |
| Damage & Health | Consumer | Bus → DmgHealth | Receives HitEvent |

## Tuning Knobs

| Knob | Type | Default | Range | Notes |
|------|------|---------|-------|-------|
| Per-target hit cooldown | float | 0.3s | 0.05–1.0 | Min time between hits on same target |

## Visual/Audio Requirements

None. Hit Detection routes events. VFX, audio, and screen shake are owned by consuming systems.

## UI Requirements

None.

## Acceptance Criteria

- **GIVEN** a player projectile hits an enemy, **WHEN** `OnTriggerEnter` fires, **THEN** a `HitEvent` is published to the Event Bus with the correct attacker, target, and hit position.
- **GIVEN** a player projectile hits the same enemy twice within 0.3s, **WHEN** the second collision occurs, **THEN** no second `HitEvent` is published.
- **GIVEN** a player projectile hits another player entity (same faction), **WHEN** the collision occurs, **THEN** no `HitEvent` is published.
- **GIVEN** an enemy touches the player (contact damage), **WHEN** `OnTriggerEnter` fires, **THEN** a `HitEvent` is published with the enemy as attacker and player as target.
- **GIVEN** a hitbox's `GameObject` is destroyed mid-collision, **WHEN** `OnTriggerEnter` fires, **THEN** no exception is thrown.
- **GIVEN** a scene transitions, **WHEN** `Clear()` is called, **THEN** all registered hitboxes/hurtboxes are unregistered.

## Open Questions

1. Should we implement a debug visualization for active hitboxes (dev build only)? → **Recommendation**: Yes — draw hitbox bounds with `Gizmos.DrawWireCube` in OnDrawGizmos. Deferred to implementation.
