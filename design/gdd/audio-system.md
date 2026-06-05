# Audio System

> **Creative Director Review (CD-GDD-ALIGN)**: CONCERNS — accepted 2026-05-29 (elemental audio layering added, synergy audio deferred to Alpha)
> **Status**: Designed
> **Author**: game-designer
> **Last Updated**: 2026-05-29
> **Implements Pillar**: P1 (Rifts Tell Stories) — elemental audio identity. P3 (Snappy Sessions) — responsive audio feedback.

## Overview

The Audio System wraps the template's `AudioManager` and `SoundEffectsPool` in a VContainer-registered service layer that dispatches all game audio. It subscribes to Event Bus events (`GameStateChanged`, `DamageDealt`, `EntityDied`, `LevelUp`, `CurrencyChanged`, `LoreFragmentCollected`, `ZoneRestored`) and maps each to the appropriate SFX or music action. It manages music crossfade across GState transitions (Menu → HeroCamp → InRun → Victory/Defeat), resolves per-zone ambience and music tracks via `IZoneAudioProvider`, and plays skill-specific combat SFX via string audio keys from Skill Data. The template's existing `AudioManager` remains the master volume handler; this system provides the orchestration layer that decides what plays when.

## Player Fantasy

Every element has a voice. Fire crackles with the last passion of a dying age, Ice hums with frozen knowledge, Lightning buzzes with broken technology. Zone ambiences are the world whispering its own eulogy — the player runs through a dying memory. Combat audio lands with satisfying weight: each hit SFX, each death sound, each level-up chime tells the player their actions matter. Full elemental synergy audio (reaction sounds for multi-element combos) is deferred to Alpha — the MVP delivers per-element identity through cast SFX, hit SFX, and a subtle ambient layer when an element is active.

## Detailed Design

### Core Rules

**1. Audio key → clip resolution** — A `ScriptableObject`-based registry maps string keys to `AudioClip` references:

```csharp
[CreateAssetMenu(menuName = "TinyRift/Audio Cue Library")]
public class AudioCueLibrary : ScriptableObject
{
    public List<AudioCueEntry> entries;

    public AudioClip GetClip(string key)
    {
        // dictionary lookup, logged warning on miss, returns null
    }
}

[System.Serializable]
public struct AudioCueEntry
{
    public string key;
    public AudioClip clip;
}
```

Key naming: `{category}_{context}_{variant}` (e.g. `sfx_hit_fire_orb`, `music_zone_crystal`, `amb_zone_wasteland`). Three separate SO assets for authoring: `MusicCueLibrary`, `AmbientCueLibrary`, `SfxCueLibrary` — merged into a single dictionary at startup.

**2. Music crossfade** — `MusicController` owns two independent `AudioSource` components on a `DontDestroyOnLoad` GameObject created at VContainer bootstrap:
- At most one active track at a time.
- `CrossfadeTo(nextKey, duration)`: if no track → play on source A. If same track → no-op. If different → fade inactive source to 1.0, active to 0.0 simultaneously over `duration` seconds, stop previous, swap designation.
- Uses `AnimationCurve` (editable, default logarithmic out/in) for fade shape.
- Only one crossfade in-flight at a time. New call cancels and replaces in-flight, capturing current volumes as new fade start.
- All fades use `UniTask` for cancellation support.
- `Duck(targetVolume, duration)` / `Unduck(duration)` — pause/resume ducking with independent state tracking.

**3. Event Bus → audio action mapping:**

| Event | Handler | Audio Key Resolution | Volume Tag |
|-------|---------|---------------------|------------|
| `GameStateChangedEvent` | `OnGameStateChanged()` | `music_{newState}` for crossfade, `sfx_state_{newState}` for transition SFX | master |
| `DamageDealtEvent` | `OnDamageDealt()` | `SkillData.HitAudioCueKey` if skillId set, else `sfx_hit_{element}` | vfx |
| `EntityDiedEvent` | `OnEntityDied()` | `sfx_death_{entityType}`, fallback `sfx_death_generic` | vfx |
| `ZoneRestoredEvent` | `OnZoneRestored()` | `sfx_zone_restore_harmonic` | master |
| `CurrencyChangedEvent` | `OnCurrencyChanged()` | `sfx_coin_clink` (only if delta > 0) | vfx |
| `LevelUpEvent` | `OnLevelUp()` | `sfx_levelup_chime` | master |
| `LoreFragmentCollectedEvent` | `OnLoreCollected()` | `sfx_lore_collect_stinger` | master |
| `ElementalReactionEvent` (Alpha) | `OnElementalReaction()` | `sfx_synergy_{type}` — deferred | master |

**4. Zone audio resolution** — On `Loading → InRun` transition, resolves `ZoneId` from `GameStateContext`, calls `IZoneAudioProvider.GetAmbienceId(zoneId)` and `IZoneAudioProvider.GetMusicTrackId(zoneId)`, then plays ambience and crossfades to zone music.

**5. Volume tag convention:**
- Music → tag `"master"` (controlled by `masterVolume`)
- Ambience → tag `"ambient"` (controlled by `ambienceVolume`)
- SFX → tag `"vfx"` (controlled by `vfxVolume`)

**6. Template integration** — Our `MusicController` manages independent audio sources; we do NOT call `AudioManager.StopAllAudioPlay()` (it would kill our music sources). Template's `SceneAmbientAudio` may co-exist using `AudioManager.ambientAudioSource` for environmental loops. Our one-shot SFX calls delegate via `ITinyRiftAudioService.PlayOneShot()` → `AudioManager.PlayAudio()` → `SoundEffectsPool`.

**7. Elemental audio layering** — When the player has at least one skill of a given element equipped, a subtle ambient layer for that element plays under the combat music. Controlled by `ITinyRiftAudioService.PlayElementAmbience(element)` / `StopElementAmbience(element)`. The ambience is a low-mix drone/loop (fire crackle, ice hum, lightning buzz) that intensifies with more skills of that element. This delivers the "voice of a dying age" fantasy without significant runtime scope.

**8. Synergy audio** — Deferred to Alpha alongside the Synergy System (#40). When synergy reactions are implemented, `ElementalReactionEvent` will be added to the Event Bus mapping with a reaction SFX key `sfx_synergy_{type}`. No MVP work required.

### States and Transitions (Music State Machine)

| Transition | Duration | Behavior |
|-----------|----------|----------|
| Idle → Menu | 1.5s | Fade-in menu music |
| Menu → HeroCamp | 2.0s | Crossfade |
| HeroCamp → Menu | 1.5s | Crossfade |
| HeroCamp → Zone | 2.0s | Crossfade starts on `InRun` entry (loading complete) |
| Zone → Paused | 0.3s | Duck active track to 20% |
| Paused → Zone | 0.3s | Unduck to 100% |
| Zone → Victory | 0.5s | Fade out combat → victory fanfare (one-shot). After fanfare (~3s), crossfade 2.0s to HeroCamp music |
| Zone → Defeat | 0.5s | Fade out combat → defeat sting (one-shot). After sting (~2s), crossfade 2.0s to HeroCamp music |
| Any → Loading | 0.3s | Quick fade-out of current track |

One-way progression: `Idle → Menu → HeroCamp → Zone → Victory/Defeat → HeroCamp/Menu`.

### Interactions with Other Systems

```csharp
public interface ITinyRiftAudioService
{
    void PlayMusic(string musicKey, float crossfadeDuration = 2.0f);
    void StopMusic(float fadeOutDuration = 0.5f);
    void DuckMusic(float targetVolume = 0.2f, float fadeDuration = 0.3f);
    void UnduckMusic(float fadeDuration = 0.3f);
    void PlayAmbience(string ambienceKey, float crossfadeDuration = 1.0f);
    void StopAmbience(float fadeOutDuration = 0.5f);
    void PlayOneShot(string sfxKey, Vector3? worldPos = null, float volumeScale = 1.0f);
    void SetMasterVolume(float value);
    void SetVFXVolume(float value);
    void SetAmbienceVolume(float value);
}
```

| System | Direction | Interface | What Flows |
|--------|-----------|-----------|------------|
| Event Bus (#5) | Inbound | Subscription to 7 event types | State transitions, combat events, game events |
| Zone Definition (#12) | Outbound (query) | `IZoneAudioProvider` | Ambience + music track IDs per zone |
| Skill Data (#6) | Outbound (query) | `SkillData.AudioCueKey` / `HitAudioCueKey` | String keys for per-skill cast/hit SFX |
| AudioManager (template) | Outbound (delegate) | Singleton (not DI) | Volume setters, `PlayAmbientAudio()`, `PlayAudio()` |
| SoundEffectsPool (template) | Outbound (delegate) | Singleton pool | Pooled one-shot SFX AudioSources |
| SkillPresentationAdapter (#34) | Inbound | `ITinyRiftAudioService.PlayOneShot()` | Cast SFX at skill use moment |
| GState (#2) | Inbound | Via Event Bus | State enum for music crossfade |
| Save/Profile (#10) | Soft | AudioManager persists volume to SecurePrefs | Volume settings persistence |

## Formulas

None. Volume is a simple multiplication (master × category). Crossfade timing is a tuning knob, not a formula.

## Edge Cases

- **If an audio key is not found in any cue library**: The dictionary lookup logs a warning and returns `null`. `PlayOneShot()` silently skips null clips. No crash, no error sound.

- **If an `AudioCueEntry` has a valid key but null `AudioClip` reference**: Treated as "not authored yet." Logged as a warning once per key per session. Not an error — supports incremental authoring.

- **If a second `CrossfadeTo()` is called while a crossfade is in-flight**: The in-flight crossfade is cancelled. Current volumes of both sources are captured as the starting point for the new crossfade. No stutter, no double-fade.

- **If `Duck()` is called during a crossfade**: Duck state is tracked independently. The duck target volume is applied as a multiplier on top of the crossfade's current values. `Unduck()` restores the crossfade's target volume (not necessarily 1.0, if the crossfade is still mid-progress).

- **If the concurrent SFX limit is reached (SoundEffectsPool max 32)**: The pool's existing behavior applies — oldest AudioSource is recycled. No crash, no missed audio guarantee. This is a template behavior, not overridden.

- **If a state transition happens before the previous transition's audio completes** (e.g., HeroCamp → Zone → Victory in quick succession): Each transition cancels the previous music state via `CrossfadeTo()` replace behavior. Queue depth is 1 → the most recent transition wins.

- **If the player sets Master volume to 0**: All audio is silent. This is expected — the player chose silence. No side effects.

- **If a zone has no `IZoneAudioProvider` entry** (Zone Definition doesn't define ambience/music for this zone): Fallback keys are used: `music_zone_default` for music, `amb_zone_default` for ambience. These exist in the cue libraries as safety-net entries.

- **If `SceneAmbientAudio` (template) fires alongside our zone audio**: Template's `SceneAmbientAudio` plays on `AudioManager.ambientAudioSource` with an ambient clip from the scene's `SceneAmbientAudio` component. Our `PlayAmbience()` also targets the ambientAudioSource. If both fire, the second call replaces the first. Our system loads zone ambience via `PlayAmbience()` on zone entry, before `SceneAmbientAudio.Start()` runs — ours wins.

- **If the game is paused while audio is ducked**: Duck state persists through pause. `Unduck()` on unpause restores the correct volume. No double-ducks.

- **If a crossfade UniTask is cancelled during scene unload or scope dispose**: The task's cancellation token fires. Crossfade stops at current volume. The next music call starts fresh from that position.

## Dependencies

### Hard Dependencies

| System | # | Nature |
|--------|---|--------|
| Event Bus | 5 | Subscribes to 7 event types for audio dispatch |
| Zone Definition System | 12 | Queries `IZoneAudioProvider` for per-zone ambience/music keys |
| Skill Data System | 6 | Reads `AudioCueKey` and `HitAudioCueKey` string keys |
| Game State Manager | 2 | Provides state transitions via `GameStateChangedEvent` |
| AudioManager (template) | — | Singleton for master/VFX/ambience volume, ambient playback, one-shot API |
| SoundEffectsPool (template) | — | Pooled AudioSources for concurrent SFX |

### Soft Dependencies

| System | # | Nature |
|--------|---|--------|
| SkillPresentationAdapter | 34 | Consumes `ITinyRiftAudioService.PlayOneShot()` for cast SFX |
| Synergy System (#40, Alpha) | — | Future consumer of `ElementalReactionEvent` for synergy reaction SFX |
| Save/Profile | 10 | Volume settings persisted via `AudioManager`'s SecurePrefs mechanism |
| Scene Event Bus | — | `SceneAmbientAudio` (template) co-exists on `ambientAudioSource` |

### Bidirectional Consistency

- Event Bus lists "Audio System — Consumer" for 7 event types (✓ matches this GDD)
- Zone Definition lists `IZoneAudioProvider` and "Audio System (#14) — Outbound — Ambience + music track IDs" (✓ matches)
- Skill Data lists `AudioCueKey` and `HitAudioCueKey` for per-skill audio (✓ matches)
- Game State Manager lists "Audio System — Subscribes to `GameStateChanged` → crossfade music" (✓ matches)

## Tuning Knobs

| Knob | Field | Type | Range | Default | Owner |
|------|-------|------|-------|---------|-------|
| Menu → Camp crossfade | `crossfadeDurationMenuCamp` | float | 0.5–4s | 2.0s | Audio designer |
| Camp → Zone crossfade | `crossfadeDurationCampZone` | float | 0.5–4s | 2.0s | Audio designer |
| Zone → Victory fade | `fadeOutDurationVictory` | float | 0.1–2s | 0.5s | Audio designer |
| Zone → Defeat fade | `fadeOutDurationDefeat` | float | 0.1–2s | 0.5s | Audio designer |
| Duck volume | `duckTargetVolume` | float | 0.0–1.0 | 0.2 | Audio designer |
| Duck/unduck speed | `duckFadeDuration` | float | 0.1–1s | 0.3s | Audio designer |
| Idle → Menu fade-in | `fadeInDurationMenu` | float | 0.5–4s | 1.5s | Audio designer |
| Crossfade curve | `crossfadeCurve` | AnimationCurve | — | Log out → log in | Audio designer |

All knobs live on `MusicController`'s serialized fields, editable in the Inspector on its prefab.

## Acceptance Criteria

### Music Crossfade

- **AC1** — **GIVEN** the app starts, **WHEN** `GameStateChanged(→Menu)` fires, **THEN** `music_menu` plays on the active music source at full volume within 1.5s.

- **AC2** — **GIVEN** the player transitions from HeroCamp to a zone, **WHEN** `GameStateChanged(InRun)` fires, **THEN** `MusicController.CrossfadeTo(zoneMusicKey, 2.0s)` is called AND the zone music becomes the active track after the fade completes.

- **AC3** — **GIVEN** the player pauses, **WHEN** `GameStateChanged(Paused)` fires, **THEN** the active music volume ducks to 20% over 0.3s. **WHEN** the player unpauses, **THEN** volume restores to full over 0.3s.

- **AC4** — **GIVEN** the player completes a zone (Victory), **WHEN** the Victory fanfare one-shot finishes (~3s), **THEN** `CrossfadeTo(music_camp, 2.0s)` begins.

### Zone Audio

- **AC5** — **GIVEN** the player enters `zone_crystal_caverns`, **WHEN** `GameStateChanged(InRun)` fires, **THEN** `IZoneAudioProvider.GetAmbienceId("zone_crystal_caverns")` and `GetMusicTrackId("zone_crystal_caverns")` are called AND the returned ambience plays on the ambient source AND the returned music plays on the music source.

- **AC6** — **GIVEN** a zone has no `IZoneAudioProvider` entry, **WHEN** zone entry occurs, **THEN** `music_zone_default` plays for music AND `amb_zone_default` plays for ambience.

### Event SFX

- **AC7** — **GIVEN** `DamageDealtEvent` fires with a `skillId`, **WHEN** the Audio System processes the event, **THEN** the clip at the skill's `HitAudioCueKey` is played via `PlayOneShot()` at the event's world position.

- **AC8** — **GIVEN** `DamageDealtEvent` fires without a `skillId` but with an `element`, **WHEN** processed, **THEN** `sfx_hit_{element}` is played. **GIVEN** the element is `Fire`, **THEN** `sfx_hit_fire` plays.

- **AC9** — **GIVEN** `EntityDiedEvent` fires, **WHEN** processed, **THEN** `sfx_death_{entityType}` plays at the death position. **GIVEN** the entity type has no dedicated death SFX, **THEN** `sfx_death_generic` plays.

- **AC10** — **GIVEN** `CurrencyChangedEvent` fires with `delta > 0`, **WHEN** processed, **THEN** `sfx_coin_clink` plays. **GIVEN** `delta ≤ 0`, **THEN** no SFX plays.

- **AC11** — **GIVEN** `LevelUpEvent` fires, **WHEN** processed, **THEN** `sfx_levelup_chime` plays.

- **AC12** — **GIVEN** `LoreFragmentCollectedEvent` fires, **WHEN** processed, **THEN** `sfx_lore_collect_stinger` plays.

### Error Handling

- **AC13** — **GIVEN** an audio key is not found in any cue library, **WHEN** `PlayOneShot(missingKey)` is called, **THEN** no clip plays AND a warning is logged once per missing key per session.

- **AC14** — **GIVEN** `CrossfadeTo()` is called during an active crossfade, **WHEN** the new call arrives, **THEN** the in-flight crossfade is cancelled AND the new crossfade starts from current volumes.

### Volume Persistence

- **AC15** — **GIVEN** the player sets Master volume to 0.5, **WHEN** the app restarts, **THEN** `AudioManager.Singleton.masterVolume` reads 0.5 from SecurePrefs AND the effective volume reflects the restored value.
