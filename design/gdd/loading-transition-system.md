# Loading & Transition System

> **Status**: Designed

> **System ID**: #35 | **Layer**: UI | **MVP**: Yes
> **Depends on**: Scene Manager (#9), Game State (#1), VFX (#15)

## 1. Overview

The Loading & Transition System manages scene transitions with visual loading screens and between-scene VFX (ink-stamp, fade, parchment-tear). It provides a consistent transition experience between Hero Camp, zones, and run flow.

## 2. Detailed Rules

- `ITransitionService` — injectable, provides `TransitionTo(SceneKey, TransitionType)`
- Transition types: `FadeToBlack` (0.5s), `InkStamp` (1.0s — parchment-tear VFX, deferred), `Instant` (no transition, dev only)
- Flow: scene unload → loading screen → load scene → init systems → transition out
- Loading screen: dark background + zone name + lore snippet (if available) + progress indicator
- Scene Manager provides the target scene reference; Transition Service handles the visual wrapper
- Loading screen is a special additive scene with its own UI canvas
- No async loading progress bar in MVP — loading is fast enough for small scenes; show spinner or zone name only
- Transition VFX (ink stamp, feather particles) uses VFX System pooled effects

## 3. ACs

1. TransitionTo loads target scene with specified transition type
2. Loading screen shows during transition with zone name
3. FadeToBlack transition takes 0.5s
4. InkStamp transition deferred (falls back to FadeToBlack)
5. Scene loads correctly after transition completes
6. Game state is InTransition during loading, resolves to target state on completion
