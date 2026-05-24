# Product Brief — Tiny Rift Survivors

## Elevator Pitch

A pixel-art bullet-heaven survivor-like where the player channels elemental rifts
to unleash devastating skill combinations against waves of void-spawned enemies.
Online from day one with server-authoritative economy via WebSocket + SQL backend.

## Current Project Identity

| Field | Current | Target |
|-------|---------|--------|
| Product Name | `Tiny-Rift-Survivors-GameClient` | `Tiny Rift Survivors` |
| Company Name | `DefaultCompany` | To be decided |
| Bundle ID | `com.DefaultCompany.Tiny-Rift-Survivors-GameClient` | `com.[studio].tinyrift` |

## Genre

- Top-down 2D survivor-like (Vampire Survivors-like)
- Bullet heaven (player is the bullet hell)
- Roguelite with persistent online progression

## Core Pillars

1. **Build-Crafting** — Elemental skill synergies create emergent builds every run
2. **Power Fantasy** — From underpowered survivor to screen-clearing force
3. **Snappy Runs** — 20–30 minute sessions, always something meaningful to choose

## Backend Approach

| Service | Role | Status |
|---------|------|--------|
| WebSocket + SQL | Primary production backend | M0 |
| Offline | Dev/test/fallback | M0 |
| Firebase | Deferred | Not planned |
| Fusion 2 Multiplayer | Deferred | Future |
| IAP / Battle Pass | Deferred | Future |

## Monetization

Premium purchase only. No IAP, no ads.
Server-authoritative currency prevents local economy tampering.

## Platform

- **Primary**: PC (Steam)
- **Engine**: Unity 6 (URP, 2D)
- **Backend**: Node.js + Colyseus + MySQL
- **Release**: Early Access → Full Release
