# Backend Data Ownership — Tiny Rift Survivors

This document maps which tables store which domain data and which JSON/data files
seed gameplay content.

---

## Database Tables (Server-Side)

### Accounts & Auth

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `users` | Account | Auth system | Core identity: email, password_hash, guestPass, role, ban status, created_at, last_login |
| `sessions` | Auth | Auth system | Active JWT sessions, expiry, refresh tokens |

**Client validation:** `GET auth/me` validates JWT. `SecurePrefs` stores token + email + userId locally.

---

### Profiles

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `profiles` | Player Profile | Profile system | displayName, selectedCharacterId, favouriteCharacterId, iconId, frameId, accountLevel, accountCurrentExp |

**Updated by:** Change name/icon/frame, character select/favourite, account XP.

---

### Currency

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `currencies` | Economy | Currency service | `userId` (PK), `gold`, `gems`, `total_gold_earned`, `total_gem_earned`, `version` (optimistic concurrency) |

**Server-authoritative.** All mutations validated server-side:
- `POST auth/purchase/shop` — deduct, grant items
- `POST auth/progress/session` — add session gold
- `POST auth/mail/claim` — grant from mail attachments
- `POST auth/rewards/*` — grant from reward claims
- `POST auth/coupon/redeem` — grant from coupon

---

### Characters

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `characters` | Character Progression | Character system | Per-character level, currentExp, masteryLevel, masteryCurrentExp, selectedSkinId |
| `character_skins` | Cosmetics | Character system | Unlocked skins per character (many-to-many) |
| `character_slots` | Equipped Items | Character system | Item slots per character (slotName → item GUID mapping) |
| `character_stats` | Permanent Upgrades | Character system | Upgraded stats per character (statType → level) |

**Loaded via:** `GET auth/init` → `charactersData[]` array.
**Updated by:** Level up, stat upgrade, skin unlock/select, slot equip.

---

### Inventory

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `owned_items` | Catalog Ownership | Inventory system | Which shop items/icons/frames/characters the player owns (catalog IDs) |
| `inventory_items` | Instance Items | Inventory system | Instanced items with GUID, templateItemId, itemLevel, upgrades |

**Loaded via:** `GET auth/init` → `owned{}` + `inventoryItems[]`.
**Updated by:** Shop purchase, battle pass claim, loot drops, inventory upgrade.

---

### Shop & Purchasing

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `shop_purchases` (inferred) | Commerce | Purchase system | Purchase transaction history |
| `iap_receipts` (inferred) | IAP | Purchase system | Receipt validation records |

**Seeded by:** `ShopItem` ScriptableObjects (exported to server via DataExport tools).
**Note:** IAP tables are in template design but deferred for our MVP.

---

### Battle Pass

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `battle_pass_progress` | Progression | Battle pass system | level, currentXp, premium (bool), claimedBits (bitmask) |

**Loaded via:** `GET auth/init` → `progress.battlePass{}` + `progress.battlePassMeta{}`.
**Updated by:** Battle pass XP, premium unlock, claim reward.
**Seeded by:** `BattlePassItem` ScriptableObjects.

---

### Progress & History

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `session_history` (inferred) | Game History | Progress system | Per-run records: mapId, characterId, monstersKilled, goldGained, won, timestamp |
| `progress` | Player Progress | Progress system | score, unlockedMaps (serialized), quest states |
| `quests` | Quests | Quest system | Individual quest progress (questId, progress, completed, questType) |

**Loaded via:** `GET auth/init` → `progress{}`.
**Updated by:** Session complete, quest complete/refresh.

---

### Rewards

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `daily_rewards` | Daily Login | Rewards system | Per-cycle claim tracking: firstClaimed, lastClaimed, claimedBits |
| `new_player_rewards` | Onboarding | Rewards system | Per-player new join reward tracking |
| `map_rewards` | Map Completion | Rewards system | Claimed map completion rewards |
| `used_coupons` | Coupons | Rewards system | Redeemed coupon codes per player |

**Loaded via:** `GET auth/init` → `rewards{}` + `usedCoupons[]` + `claimedMapRewards[]`.
**Seeded by:** Reward template ScriptableObjects in GameInstance.

---

### Leaderboards

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `leaderboard_entries` | Ranking | Leaderboard system | userId, wave, score, character_used, achieved_at |

**Read via:** `GET auth/ranking/top`, `GET auth/ranking/my`.
**Written via:** `POST auth/progress/session` → score update.

---

### Friends & Social

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `friends` | Social Graph | Friends system | Bidirectional friend relationships |
| `friend_requests` | Social | Friends system | Pending friend requests (incoming, outgoing) |
| `blocked_users` | Moderation | Friends system | Blocked user records |

**Presence** is in-memory (via `presence_room` Colyseus room state), not a persistent table.

---

### Mail

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `mail_inbox` | Messaging | Mail system | Per-player inbox items with status (UNREAD/READ/CLAIMED) |
| `mail_messages` | Messaging | Mail system | Message templates (title, body, sender, attachments) |

**Attachments types:** `Currency`, `Icon`, `Frame`, `Character`, `InventoryItem`.

---

### GM / Admin

| Table | Domain | Owned By | Description |
|-------|--------|----------|-------------|
| `global_messages` (inferred) | Admin | GM system | Current global announcement (title, text, duration, expiry) |
| `map_events` (inferred) | Admin | GM system | Active map events (eventId, mapId, name, description, duration) |

---

## JSON / Data Files (Seed Data)

The template exports gameplay data from Unity ScriptableObjects to JSON for the server.
These live under `BulletHellTemplate/Res/GameData/` and are exported via `DataExport/*` editor tools.

### Game Configuration Seed Data

| File | Contents | Consumed By |
|------|----------|-------------|
| `GameData/*.json` | Game constants, XP tables, level configs | GameInstance |
| `CharacterData.json` | Character definitions (stats, growth curves) | Character system |
| `SkillData.json` | Skill definitions, damage formulas | Skill system |
| `ShopItem.json` | Shop catalog (items, prices, currency type) | Shop/Purchase system |
| `MapInfo.json` | Map definitions (arena configs, enemy compositions) | Map system |
| `QuestItem.json` | Quest definitions (objectives, rewards, conditions) | Quest system |
| `CouponItem.json` | Coupon definitions (codes, rewards, limits) | Coupon system |
| `DailyRewards.json` | Daily reward calendar (day-indexed rewards) | Daily reward system |
| `BattlePassItem.json` | Battle pass reward tiers | Battle pass system |
| `InventoryItem.json` | Inventory item templates (stats, upgrade paths) | Inventory system |
| `IAPItem.json` | IAP product definitions | IAP system (deferred) |

### Export Flow

```
Unity Editor (ScriptableObject data)
  └── DataExport editor tools
        └── JSON files exported to local folder (BackendSettings.localExportFolder)
              └── Server loads these JSON files into database on startup / migration
```

The server is expected to consume exported JSON at startup or during setup.
This creates the gameplay catalog that the client's `GameInstance` ScriptableObject
matches.

## Data Ownership Summary

| Who | Owns |
|-----|------|
| **Server (MySQL)** | users, currencies, leaderboard_entries, session_history, mail transactions, shop transactions, friend relationships, mod actions |
| **Client (PlayerSave + SecurePrefs)** | JWT token, cached profile, cached currencies, cached owned items, cached characters, cached progress, cached rewards |
| **Server (JSON seed)** | Gameplay catalog: character definitions, skill data, shop items, maps, quests, coupons, rewards, battle pass tiers, inventory templates |

## Client-Side Persistence (Offline Fallback)

When using `OfflineBackendService`, all data is persisted locally via:

| Mechanism | What It Stores |
|-----------|----------------|
| `SecurePrefs` (encrypted PlayerPrefs) | Auth token, userId, email, guest pass |
| `PlayerSave` (partial classes) | Profile, currencies, owned items, characters, progress, quest states, rewards, coupons |

The `OfflineBackendService` implements the full `IBackendService` interface for
dev/test/fallback but skips server validation (local-only operations).
