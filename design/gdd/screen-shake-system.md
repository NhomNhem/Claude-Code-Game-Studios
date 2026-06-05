# Screen Shake & Feedback

> **CD-GDD-ALIGN**: N/A (pure P3 utility)
> **Status**: Designed

> **System ID**: #27 | **Layer**: Gameplay | **MVP**: Yes
> **Depends on**: Event Bus (#2), Game State (#1)
> **Depended by**: HUD (#30)

## 1. Overview

Screen shake provides hit feedback and dramatic emphasis via camera displacement. Consumes `DamageDealtEvent` (player hit = big shake, enemy hit = small shake) and `EntityDiedEvent` (boss death = dramatic shake). Also handles hit-stop (brief time freeze on heavy hits).

## 2. Player Fantasy

Every hit has weight. When you get hit, the screen punches. When a boss dies, the arena trembles. Feedback is immediate and visceral.

## 3. Detailed Rules

- `IScreenShakeService` — injectable, drives camera offset via `Cinemachine Impulse` or manual transform offset
- Shake profile: `duration`, `intensity`, `frequency`, `decay` per event type
- Hit-stop: on player hit, Time.timeScale = 0 for 0.1s, then resume. Configurable per damage source.
- Shake events queue — if 2 shakes fire in one frame, the stronger one wins
- No shake during pause, menus, or zone transitions

**Event → Shake Mapping:**
| Event | Type | Intensity | Duration | Hit-stop |
|-------|------|-----------|----------|----------|
| `DamageDealtEvent` (player target) | Punch | 0.5 | 0.2s | 0.1s |
| `DamageDealtEvent` (enemy target) | Micro | 0.1 | 0.05s | None |
| `EntityDiedEvent` (elite) | Medium | 0.3 | 0.15s | None |
| `EntityDiedEvent` (boss) | Heavy | 0.8 | 0.5s | 0.2s |
| `BossEncounter.Spawn` | Rumble | 0.4 | 1.0s | None |

## 4. Tuning Knobs

| Knob | Default | Range |
|------|---------|-------|
| Player hit intensity | 0.5 | 0.1–1.0 |
| Player hit-stop duration | 0.1s | 0.0–0.3s |
| Boss death intensity | 0.8 | 0.5–1.0 |

## 5. ACs

1. Player hit triggers punch shake + hit-stop
2. Boss death triggers heavy shake + hit-stop
3. Enemy hit triggers micro shake only
4. No shake during pause
5. Simultaneous shakes use strongest intensity
6. Hit-stop pauses game timer (Time System) for configured duration
