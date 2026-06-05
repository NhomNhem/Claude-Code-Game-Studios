# Story 002: Music Crossfade & Zone Ambience

- **Epic**: Audio System
- **System**: Audio System
- **Type**: Integration
- **Priority**: P1
- **Estimate**: 3h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-audio-002` | Music crossfade between zones and camp | ✅ ADR-002 |

## ADR Guidance

**ADR-002 (Event Bus Contract):**
- Consumes `GameStateChangedEvent` for state-driven music transitions
- Consumes `ZoneRestoredEvent` for zone ambient changes

**Control Manifest (relevant rules):**
- `MusicController` owns two independent `AudioSource` components on a `DontDestroyOnLoad` GameObject
- Crossfade uses `UniTask` for cancellation support
- Zone audio resolved via `IZoneAudioProvider` interface

## Description

Implement music crossfade across all GState transitions (Menu → HeroCamp → InRun → Victory/Defeat) and per-zone ambience resolution. `MusicController` manages two independent `AudioSource` components with crossfade via `AnimationCurve`. Ducking supports pause transitions. Zone audio keys are resolved via `IZoneAudioProvider` on `InRun` entry.

## Design

```csharp
public class MusicController : IDisposable
{
    public void CrossfadeTo(string musicKey, float duration);
    public void StopMusic(float fadeOutDuration);
    public void DuckMusic(float targetVolume, float fadeDuration);
    public void UnduckMusic(float fadeDuration);
}
```

### Music State Machine Transition Table

| Transition | Duration | Behavior |
|-----------|----------|----------|
| Idle → Menu | 1.5s | Fade-in menu music |
| Menu → HeroCamp | 2.0s | Crossfade |
| HeroCamp → Zone | 2.0s | Crossfade starts on `InRun` entry |
| Zone → Paused | 0.3s | Duck active track to 20% |
| Paused → Zone | 0.3s | Unduck to 100% |
| Zone → Victory | 0.5s → fanfare → 2.0s | Fade out → victory fanfare (one-shot) → crossfade to camp |
| Zone → Defeat | 0.5s → sting → 2.0s | Fade out → defeat sting (one-shot) → crossfade to camp |
| Any → Loading | 0.3s | Quick fade-out of current track |

### Zone Ambience Resolution

On `GameStateChanged(InRun)`:
1. Resolve `ZoneId` from `GameStateContext`
2. Call `IZoneAudioProvider.GetAmbienceId(zoneId)` and `IZoneAudioProvider.GetMusicTrackId(zoneId)`
3. Play ambience on ambient source via `PlayAmbience()`
4. Crossfade to zone music via `CrossfadeTo(zoneMusicKey, 2.0s)`
5. If no `IZoneAudioProvider` entry exists, use fallback keys `music_zone_default` / `amb_zone_default`

### Elemental Audio Layering

When player has at least one skill of a given element equipped, a subtle ambient layer for that element plays under combat music. Controlled by `PlayElementAmbience(element)` / `StopElementAmbience(element)`. The ambience is a low-mix drone/loop that intensifies with more skills of that element.

## Acceptance Criteria

1. **Menu music on start**: When `GameStateChanged(→Menu)` fires, `music_menu` plays on the active music source at full volume within 1.5s.
2. **Zone music crossfade**: When transitioning HeroCamp → InRun, `CrossfadeTo(zoneMusicKey, 2.0s)` is called and zone music becomes the active track after fade completes.
3. **Pause duck/unpause unduck**: When `GameStateChanged(Paused)` fires, active music ducks to 20% over 0.3s. On unpause, volume restores to full over 0.3s.
4. **Victory fanfare → camp crossfade**: When Victory fires, after fanfare one-shot finishes (~3s), `CrossfadeTo(music_camp, 2.0s)` begins.
5. **Zone ambience resolution**: When entering `zone_crystal_caverns`, `IZoneAudioProvider.GetAmbienceId()` and `GetMusicTrackId()` are called and the returned ambience/music plays.
6. **Fallback keys for undefined zones**: When a zone has no `IZoneAudioProvider` entry, `music_zone_default` and `amb_zone_default` play.
7. **In-flight crossfade cancellation**: When `CrossfadeTo()` is called during an active crossfade, the in-flight fade is cancelled and new crossfade starts from current volumes.
8. **Elemental ambience layering**: `PlayElementAmbience(Fire)` starts a low-mix fire crackle drone; `StopElementAmbience(Fire)` stops it cleanly.
9. **Duck state survives pause cycles**: Duck persists through pause→unpause. `Unduck()` restores to the correct pre-duck volume.
10. **Crossfade UniTask cancellation on scene unload**: Cancellation token fires, crossfade stops at current volume, next call starts fresh.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/AudioSystem/MusicCrossfadeTests.cs`
- Crossfade timing, cancellation, and replace behavior
- Duck/unduck state tracking
- Zone audio resolution with fallback keys

## Dependencies

- **Audio Story 001** — Event Bus subscription infrastructure, `ITinyRiftAudioService` interface, `AudioCueLibrary`
- **Zone Definition System** — `IZoneAudioProvider` for per-zone ambience/music key resolution
- **Game State Manager** — `GameStateChangedEvent` for state-driven transitions

## Unlocks

- None (final audio story)

## Risks

- **MEDIUM**: `SceneAmbientAudio` (template) may co-exist on `ambientAudioSource`. Our `PlayAmbience()` loads zone ambience on zone entry before `SceneAmbientAudio.Start()` runs — ours wins. Mitigation: document order dependency.
- **LOW**: Elemental audio layering adds 6 extra AudioSource instances (one per element). 6 × drone loop = negligible perf cost.
