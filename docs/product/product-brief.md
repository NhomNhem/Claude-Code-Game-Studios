# Product Brief — Tiny Rift Survivors

## Elevator Pitch

A pixel-art bullet-heaven survivor-like where the player channels elemental rifts
to unleash devastating skill combinations against waves of void-spawned enemies.
Each run builds power through smart upgrades and synergies.

## Current Project Identity

| Field | Current | Target |
|-------|---------|--------|
| Product Name | `Tiny-Rift-Survivors-GameClient` | `Tiny Rift Survivors` |
| Company Name | `DefaultCompany` | To be decided |
| Bundle ID | `com.DefaultCompany.Tiny-Rift-Survivors-GameClient` | `com.[studio].tinyrift` |

## Genre

- Top-down 2D survivor-like (Vampire Survivors-like)
- Bullet heaven (player is the bullet hell)
- Roguelite with persistent upgrade progression

## Core Pillars

1. **Build-Crafting** — Elemental skill synergies create emergent builds every run
2. **Power Fantasy** — From underpowered survivor to screen-clearing force
3. **Snappy Runs** — 20–30 minute sessions, always something meaningful to choose

## Development Approach

The BulletHell Elemental Template provides a **complete game framework** with ~250+ scripts.
We are extending and configuring, not building from scratch. All template systems
(movement, combat, skills, enemies, waves, save/load, pooling, localization, shop, inventory)
are already implemented. Our work is content creation, configuration, and custom system addition.

## Two-Track System

| Area | Public Release | Full-Stack Lab |
|------|---------------|----------------|
| Gameplay | Core survivor loop (extend template) | Multiplayer co-op (already built in template) |
| Progression | Local progression (extend PlayerSave) | Cloud sync (already built in template) |
| Backend | None — strip from build | Firebase / WebSocket (already built in template) |
| Monetization | Premium purchase only | IAP cosmetics (already built in template) |
| Networking | None | Fusion 2 + Colyseus (already built in template) |
| Build defines | `UNITY_PIPELINE_URP` | `UNITY_PIPELINE_URP;LAB_TRACK` |
