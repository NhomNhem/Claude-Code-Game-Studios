# Story 001: Event Bus Consumer & SFX Dispatch

- **Epic**: Audio System
- **System**: Audio System
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-audio-001` | SFX playback via Event Bus consumption (7 event types) | ✅ ADR-002 |
| `TR-audio-003` | Mixer bus management (master/sfx/music volume) | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `ITinyRiftAudioService` registers as interface singleton in TinyRiftScope
- `IEventBus` / `ISubscriber` injected via constructor
- No direct singleton access to template's `AudioManager` — wrap via service

**ADR-002 (Event Bus Contract):**
- Subscribes to 7 event types: `GameStateChanged`, `DamageDealt`, `EntityDied`, `LevelUp`, `CurrencyChanged`, `LoreFragmentCollected`, `ZoneRestored`
- All subscriptions registered in `Start()`, unregistered in `OnDestroy()` via `UnsubscribeAll(this)`

**Control Manifest (relevant rules):**
- Never modify template's `AudioManager` or `SoundEffectsPool` vendor code
- Wrap template singletons in TinyRift service layer
- Interface-first: consumers depend on `ITinyRiftAudioService`, not concrete implementations

## Description

Implement the Event Bus subscription layer for the Audio System. Consumes 7 Event Bus event types and maps each to the appropriate SFX action via string audio keys resolved from `AudioCueLibrary`. Manages mixer bus volume (master/sfx/music) via `ITinyRiftAudioService` and delegates one-shot playback to the template's `AudioManager` through a wrapped call.

## Design

```csharp
public interface ITinyRiftAudioService
{
    void PlayOneShot(string sfxKey, Vector3? worldPos = null, float volumeScale = 1.0f);
    void SetMasterVolume(float value);
    void SetVFXVolume(float value);
    void SetAmbienceVolume(float value);
}
```

### Event → SFX Mapping

| Event | Handler | Audio Key Resolution | Volume Tag |
|-------|---------|---------------------|------------|
| `GameStateChangedEvent` | `OnGameStateChanged()` | `sfx_state_{newState}` for transition SFX | master |
| `DamageDealtEvent` | `OnDamageDealt()` | `SkillData.HitAudioCueKey` if skillId set, else `sfx_hit_{element}` | vfx |
| `EntityDiedEvent` | `OnEntityDied()` | `sfx_death_{entityType}`, fallback `sfx_death_generic` | vfx |
| `ZoneRestoredEvent` | `OnZoneRestored()` | `sfx_zone_restore_harmonic` | master |
| `CurrencyChangedEvent` | `OnCurrencyChanged()` | `sfx_coin_clink` (only if delta > 0) | vfx |
| `LevelUpEvent` | `OnLevelUp()` | `sfx_levelup_chime` | master |
| `LoreFragmentCollectedEvent` | `OnLoreCollected()` | `sfx_lore_collect_stinger` | master |

### Mixer Bus Management

Three exposed volume properties (`masterVolume`, `vfxVolume`, `ambienceVolume`) delegate to template's `AudioManager` singleton. Initial values read from `SecurePrefs` on service start.

### Missing Key Handling

Dictionary lookup logs a warning once per missing key per session. `PlayOneShot()` silently skips null clips. No crash, no error sound.

## Acceptance Criteria

1. **Damage SFX by skill key**: When `DamageDealtEvent` fires with a `skillId`, the clip at the skill's `HitAudioCueKey` plays via `PlayOneShot()` at the event's world position.
2. **Damage SFX by element fallback**: When `DamageDealtEvent` fires without `skillId` but with an `element`, `sfx_hit_{element}` plays.
3. **Death SFX by entity type**: When `EntityDiedEvent` fires, `sfx_death_{entityType}` plays at death position, falling back to `sfx_death_generic` if no type-specific key exists.
4. **Currency gain SFX**: When `CurrencyChangedEvent` fires with `delta > 0`, `sfx_coin_clink` plays. When `delta <= 0`, no SFX plays.
5. **Level-up chime**: When `LevelUpEvent` fires, `sfx_levelup_chime` plays.
6. **Lore collection stinger**: When `LoreFragmentCollectedEvent` fires, `sfx_lore_collect_stinger` plays.
7. **Missing key warning**: When `PlayOneShot(missingKey)` is called, no clip plays and a warning is logged once per missing key per session.
8. **Volume setters delegate to AudioManager**: Setting master volume to 0.5 updates `AudioManager.Singleton.masterVolume` to 0.5.
9. **Subscriptions registered on Start**: After `Start()`, all 7 event types are subscribed and handled.
10. **Subscriptions unregistered on Destroy**: After `OnDestroy()`, `UnsubscribeAll(this)` is called and no further events are received.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/AudioSystem/EventBusConsumerSfxTests.cs`
- Event → SFX routing for all 7 event types
- Missing key handling and warning deduplication
- Volume setter delegation to AudioManager singleton

## Dependencies

- **Event Bus** — 7 event type subscriptions
- **IGameStateManager** — state enum for transition SFX
- **AudioCueLibrary** — ScriptableObject-based SFX key → clip resolution
- **AudioManager (template)** — singleton for one-shot playback, volume delegation

## Unlocks

- Audio Story 002 (Music Crossfade & Zone Ambience)

## Risks

- **LOW**: Template's `AudioManager.StopAllAudioPlay()` must NOT be called — it would kill our music sources (handled by MusicController, not this story)
- **LOW**: `SoundEffectsPool` max 32 concurrent SFX — oldest recycled on overflow; no crash
