# REST API Map — Tiny Rift Survivors Backend

Source: `WebSocketSqlBackendService` + `Websocket*Handler` classes in the Unity client.
Server expected at `BackendSettings.serverUrl` (default `ws://127.0.0.1:2567`).
Transport: HTTP REST via Colyseus `client.Http.Request(method, path, body)`.

---

## Auth

### POST `auth/register`

- **Auth**: None (pre-auth)
- **Service**: `WebsocketAuthHandler.RegisterAsync(email, pass)`
- **Tables**: `users`
- **Unity Feature**: Login screen — Create Account button
- **Request**:
  ```json
  { "email": "string", "password": "string" }
  ```
- **Response**:
  ```json
  { "token": "string", "user": { "id": 1, "email": "string", "guestPass": null } }
  ```

---

### POST `auth/login`

- **Auth**: None (pre-auth)
- **Service**: `WebsocketAuthHandler.LocalAsync(email, pass)`
- **Tables**: `users`
- **Unity Feature**: Login screen — Log In button
- **Request**:
  ```json
  { "email": "string", "password": "string" }
  ```
- **Response**:
  ```json
  { "token": "string", "user": { "id": 1, "email": "string", "guestPass": null } }
  ```

---

### POST `auth/anonymous`

- **Auth**: None (pre-auth)
- **Service**: `WebsocketAuthHandler.LoginGuestAsync()`
- **Tables**: `users`
- **Unity Feature**: Play as Guest button
- **Request**: no body
- **Response**:
  ```json
  { "token": "string", "user": { "id": 1, "email": null, "guestPass": "string" } }
  ```

---

### GET `auth/me`

- **Auth**: JWT required (via `Authorization: Bearer <token>`)
- **Service**: `WebsocketAuthHandler.TryAutoLoginAsync()`
- **Tables**: `users`
- **Unity Feature**: Startup — validate saved JWT on app launch
- **Request**: none (token in Authorization header)
- **Response**:
  ```json
  { "id": 1, "email": "string", "guestPass": "string" }
  ```

---

## Data Loading

### GET `auth/init`

- **Auth**: JWT required
- **Service**: `WebsocketDataLoadHandler` (fetches ALL player data)
- **Tables**: `profiles`, `currencies`, `characters`, `progress`, `rewards`, `owned_items`, `inventory_items`, `used_coupons`, `claimed_map_rewards`
- **Unity Feature**: Startup — after successful auth, loads full game state
- **Request**: none
- **Response**:
  ```json
  {
    "profile": { "displayName": "string", "selectedCharacterId": 1, "favouriteCharacterId": 1, "iconId": "string", "frameId": "string", "accountLevel": 1, "accountCurrentExp": 0 },
    "currencies": [ { "code": "GOLD", "balance": 100 } ],
    "owned": { "shopItemIds": [], "iconIds": [], "frameIds": [], "characterIds": [], "inventoryItems": [ { "uniqueItemGuid": "guid", "templateItemId": "string", "itemLevel": 1 } ] },
    "charactersData": [ { "characterId": 1, "level": 1, "currentExp": 0, "masteryLevel": 1, "masteryCurrentExp": 0, "selectedSkinId": 0, "slots": {}, "upgrades": {}, "unlockedSkins": [] } ],
    "progress": { "quests": [], "unlockedMaps": [], "score": 0, "battlePass": { "level": 1, "currentXp": 0, "premium": false, "claimedBits": 0 }, "battlePassMeta": { "season": "string", "seasonStartUtc": "date", "durationDays": 30 } },
    "rewards": { "newPlayer": { "joinedAt": "date", "lastClaimed": "date", "claimedBits": 0 }, "daily": { "firstClaimed": "date", "lastClaimed": "date", "claimedBits": 0 } },
    "usedCoupons": [],
    "claimedMapRewards": []
  }
  ```

---

## Profile

### POST `auth/profile/name`

- **Auth**: JWT required
- **Service**: `WebsocketProfileHandler.ChangePlayerNameAsync`
- **Tables**: `profiles`
- **Unity Feature**: Settings / Profile — change display name
- **Request**:
  ```json
  { "newName": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

### POST `auth/profile/icon`

- **Auth**: JWT required
- **Service**: `WebsocketProfileHandler.ChangePlayerIconAsync`
- **Tables**: `profiles`
- **Unity Feature**: Profile — change avatar icon
- **Request**:
  ```json
  { "iconId": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

### POST `auth/profile/frame`

- **Auth**: JWT required
- **Service**: `WebsocketProfileHandler.ChangePlayerFrameAsync`
- **Tables**: `profiles`
- **Unity Feature**: Profile — change avatar frame
- **Request**:
  ```json
  { "frameId": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

## Characters

### POST `auth/character/select`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.SelectCharacterAsync`
- **Tables**: `profiles`
- **Request**:
  ```json
  { "characterId": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/character/favourite`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.FavouriteCharacterAsync`
- **Tables**: `profiles`
- **Request**:
  ```json
  { "characterId": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/character/unlock-skin`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.UnlockCharacterSkinAsync`
- **Tables**: `character_skins`
- **Request**:
  ```json
  { "characterId": 1, "skinIndex": 0 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/character/set-skin`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.SetCharacterSkinAsync`
- **Tables**: `characters`
- **Request**:
  ```json
  { "characterId": 1, "skinIndex": 0 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/character/{characterId}/upgrade/{statType}`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.TryUpgradeStatAsync`
- **Tables**: `character_stats`
- **Unity Feature**: Character upgrade screen (permanent stat upgrades)
- **Request**: no body
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/character/levelup`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.LevelUpCharacterAsync`
- **Tables**: `characters`
- **Request**:
  ```json
  { "characterId": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/character/slot`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.SetCharacterSlotItemAsync`
- **Tables**: `character_slots`
- **Request**:
  ```json
  { "characterId": 1, "slotName": "string", "guid": "string", "uniqueGuid": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### DELETE `auth/character/inventory/{guid}`

- **Auth**: JWT required
- **Service**: `WebsocketCharacterHandler.DeletePurchasedItemAsync`
- **Tables**: `inventory_items`
- **Fallback**: `POST auth/character/delete-item` with `{ "guid": "string" }`
- **Request**: none (guid in URL)
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

## Inventory

### POST `auth/inventory/upgrade-item`

- **Auth**: JWT required
- **Service**: `WebsocketInventoryHandler.UpgradeInventoryItemAsync`
- **Tables**: `inventory_items`
- **Request**:
  ```json
  { "guid": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string", "newLevel": 2 }
  ```

---

## Purchasing

### POST `auth/purchase/shop`

- **Auth**: JWT required
- **Service**: `WebsocketPurchasesHandler.PurchaseShopItemAsync`
- **Tables**: `currencies`, `owned_items`, `inventory_items`
- **Unity Feature**: Shop — buy item with currency
- **Request**:
  ```json
  { "itemId": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string", "inventory": [ { "uniqueItemGuid": "guid", "templateItemId": "string", "itemLevel": 1 } ] }
  ```

---

### POST `auth/purchase/battlepass/claim`

- **Auth**: JWT required
- **Service**: `WebsocketPurchasesHandler.ClaimBattlePassRewardAsync`
- **Tables**: `battle_pass_progress`
- **Request**:
  ```json
  { "passId": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string", "inventory": [ { "uniqueItemGuid": "guid", "templateItemId": "string", "itemLevel": 1 } ] }
  ```

---

### POST `auth/purchase/battlepass/premium`

- **Auth**: JWT required
- **Service**: `WebsocketPurchasesHandler.UnlockBattlePassPremiumAsync`
- **Tables**: `battle_pass_progress`
- **Request**:
  ```json
  {}
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

### GET `auth/purchase/owned`

- **Auth**: JWT required
- **Service**: `WebsocketPurchasesHandler.RefreshOwnedDataAsync`
- **Tables**: `owned_items`, `inventory_items`
- **Unity Feature**: Refresh owned items after purchase
- **Request**: none
- **Response**:
  ```json
  { "shopItemIds": [], "iconIds": [], "frameIds": [], "characterIds": [], "inventoryItems": [ { "uniqueItemGuid": "guid", "templateItemId": "string", "itemLevel": 1 } ] }
  ```

---

## Progress

### POST `auth/progress/session`

- **Auth**: JWT required
- **Service**: `WebsocketProgressHandler.CompleteGameSessionAsync`
- **Tables**: `session_history`, `currencies`, `progress`, `map_rewards`
- **Unity Feature**: End of run — submit results
- **Request**:
  ```json
  { "mapId": 1, "characterId": 1, "monstersKilled": 100, "gainedGold": 500, "won": true }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string", "newInventoryItems": [ { "uniqueItemGuid": "guid", "templateItemId": "string", "itemLevel": 1 } ] }
  ```

---

### POST `auth/progress/quest/complete`

- **Auth**: JWT required
- **Service**: `WebsocketProgressHandler.CompleteQuestAsync`
- **Tables**: `quests`
- **Request**:
  ```json
  { "questId": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string", "currencies": [ { "code": "GOLD", "amount": 100 } ], "newInventoryItems": [] }
  ```

---

### POST `auth/progress/quest/refresh`

- **Auth**: JWT required
- **Service**: `WebsocketProgressHandler.RefreshQuestLevelProgressAsync`
- **Tables**: `quests`
- **Request**: no body
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

## Ranking / Leaderboards

### GET `auth/ranking/top?limit=N`

- **Auth**: JWT required
- **Service**: `WebsocketProgressHandler.GetTopPlayersAsync`
- **Tables**: `leaderboard_entries`
- **Unity Feature**: Leaderboard screen
- **Request**: none (query param)
- **Response**:
  ```json
  [
    { "PlayerName": "string", "PlayerIcon": "string", "PlayerFrame": "string", "PlayerCharacterFavourite": 1, "score": 1000 }
  ]
  ```

---

### GET `auth/ranking/my`

- **Auth**: JWT required
- **Service**: `WebsocketProgressHandler.GetPlayerRankAsync`
- **Tables**: `leaderboard_entries`
- **Request**: none
- **Response**:
  ```json
  { "rank": 42 }
  ```

---

## Experience

### POST `auth/exp/account`

- **Auth**: JWT required
- **Service**: `WebsocketExpHandler.AddAccountExpAsync`
- **Tables**: `profiles`
- **Request**:
  ```json
  { "amount": 100 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/exp/character`

- **Auth**: JWT required
- **Service**: `WebsocketExpHandler.AddCharacterExpAsync`
- **Tables**: `characters`
- **Request**:
  ```json
  { "characterId": 1, "amount": 100 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/exp/mastery`

- **Auth**: JWT required
- **Service**: `WebsocketExpHandler.AddCharacterMasteryExpAsync`
- **Tables**: `characters`
- **Request**:
  ```json
  { "characterId": 1, "amount": 100 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

### POST `auth/exp/battlepass`

- **Auth**: JWT required
- **Service**: `WebsocketExpHandler.AddBattlePassXpAsync`
- **Tables**: `battle_pass_progress`
- **Request**:
  ```json
  { "amount": 100 }
  ```
- **Response**:
  ```json
  { "success": true, "code": "string" }
  ```

---

## Coupons

### POST `auth/coupon/redeem`

- **Auth**: JWT required
- **Service**: `WebsocketRewardsHandler.RedeemCouponAsync`
- **Tables**: `coupons`, `used_coupons`
- **Request**:
  ```json
  { "code": "string" }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string", "currency": "GOLD", "amount": 100, "couponId": "string" }
  ```
Note: `reason` can contain pipe-delimited `"CID|amount"` as fallback format.

---

## Rewards

### POST `auth/rewards/new-player/claim`

- **Auth**: JWT required
- **Service**: `WebsocketRewardsHandler.ClaimNewPlayerRewardAsync`
- **Tables**: `new_player_rewards`
- **Request**:
  ```json
  { "dayIndex": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

### POST `auth/rewards/daily/claim`

- **Auth**: JWT required
- **Service**: `WebsocketRewardsHandler.ClaimDailyRewardAsync`
- **Tables**: `daily_rewards`
- **Request**:
  ```json
  { "dayIndex": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string" }
  ```

---

### POST `auth/map-rewards/claim`

- **Auth**: JWT required
- **Service**: `WebsocketRewardsHandler.ApplyMapRewardsAsync`
- **Tables**: `map_rewards`, `currencies`, `characters`
- **Unity Feature**: Post-run rewards screen
- **Request**:
  ```json
  { "mapId": 1, "characterId": 1 }
  ```
- **Response**:
  ```json
  { "success": true, "reason": "string", "reward": { "mapId": 1, "granted": true, "reason": "string", "currencyGrants": [ { "currencyId": "GOLD", "amount": 100 } ], "accountExp": 50, "characterExp": 30, "masteryExp": 10, "special": { "type": "Item", "id": "string" } } }
  ```

---

## Mail

### GET `auth/mail/inbox`

- **Auth**: JWT required
- **Service**: `WebsocketMailHandler.ListInboxAsync`
- **Tables**: `mail_inbox`
- **Request**: none
- **Response**:
  ```json
  { "ok": true, "data": { "data": [ { "inboxId": 1, "status": "UNREAD", "receivedAt": "date", "readAt": null, "claimedAt": null, "message": { "id": 1, "title": "string", "body": "string", "attachments": [ { "type": "Currency", "id": "GOLD", "amount": 100 } ], "expiresAt": "date", "senderName": "string", "senderRole": "GM" }, "sender": { "userId": 1, "nickname": "string", "role": "GM" } } ] } }
  ```

---

### GET `auth/mail/unread-count`

- **Auth**: JWT required
- **Service**: `WebsocketMailHandler.GetUnreadCountAsync`
- **Tables**: `mail_inbox`
- **Request**: none
- **Response**:
  ```json
  { "count": 5, "ok": true }
  ```

---

### POST `auth/mail/read`

- **Auth**: JWT required
- **Service**: `WebsocketMailHandler.MarkReadAsync`
- **Tables**: `mail_inbox`
- **Request**:
  ```json
  { "inboxId": 1 }
  ```
- **Response**:
  ```json
  { "ok": true }
  ```

---

### POST `auth/mail/claim`

- **Auth**: JWT required
- **Service**: `WebsocketMailHandler.ClaimAsync`
- **Tables**: `mail_inbox`, `currencies`, `owned_items`, `inventory_items`
- **Request**:
  ```json
  { "inboxId": 1 }
  ```
- **Response**:
  ```json
  { "ok": true, "already": false, "error": null }
  ```

---

### POST `auth/mail/delete`

- **Auth**: JWT required
- **Service**: `WebsocketMailHandler.DeleteAsync`
- **Tables**: `mail_inbox`
- **Request**:
  ```json
  { "inboxId": 1 }
  ```
- **Response**:
  ```json
  { "ok": true, "reason": null }
  ```

---

## Friends

### GET `auth/friends/list?limit=N&offset=N`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_ListAsync`
- **Tables**: `friends`
- **Request**: none (query params)
- **Response**:
  ```json
  { "ok": true, "data": [ { /* FriendSummaryData */ } ] }
  ```

---

### GET `auth/friends/pending`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_ListPendingAsync`
- **Tables**: `friend_requests`
- **Request**: none
- **Response**:
  ```json
  { "ok": true, "data": { "incoming": [ 1, 2 ], "outgoing": [ 3 ] } }
  ```

---

### GET `auth/friends/search?q={prefix}`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_SearchAsync`
- **Tables**: `users`
- **Request**: none (query param)
- **Response**:
  ```json
  { "ok": true, "data": [ { /* FriendSearchResult */ } ] }
  ```

---

### GET `auth/friends/summaries?ids=1,2,3`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_GetUserSummariesAsync`
- **Tables**: `users`, `profiles`
- **Request**: none (query param)
- **Response**:
  ```json
  { "ok": true, "data": [ { /* FriendSummaryData */ } ] }
  ```

---

### POST `auth/friends/request`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_SendRequestAsync`
- **Tables**: `friend_requests`
- **Request**:
  ```json
  { "toUserId": 2 }
  ```
- **Response**: raw JSON

---

### POST `auth/friends/accept`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_AcceptAsync`
- **Tables**: `friend_requests`, `friends`
- **Request**:
  ```json
  { "fromUserId": 1 }
  ```
- **Response**: raw JSON

---

### POST `auth/friends/reject`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_RejectAsync`
- **Tables**: `friend_requests`
- **Request**:
  ```json
  { "fromUserId": 1 }
  ```
- **Response**: raw JSON

---

### POST `auth/friends/remove`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_RemoveAsync` (+ room Send "remove")
- **Tables**: `friends`
- **Request**:
  ```json
  { "friendUserId": 2 }
  ```
- **Response**: raw JSON

---

### POST `auth/friends/block`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_BlockAsync`
- **Tables**: `blocked_users`
- **Request**:
  ```json
  { "targetUserId": 2 }
  ```
- **Response**: raw JSON

---

### POST `auth/friends/unblock`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_UnblockAsync`
- **Tables**: `blocked_users`
- **Request**:
  ```json
  { "targetUserId": 2 }
  ```
- **Response**: raw JSON

---

### GET `auth/friends/blocked`

- **Auth**: JWT required
- **Service**: `WebsocketFriendsHandler.Friends_ListBlockedAsync`
- **Tables**: `blocked_users`
- **Request**: none
- **Response**:
  ```json
  { "ok": true, "data": [ { /* FriendSummaryData */ } ] }
  ```

---

## Presence

### GET `presence/online`

- **Auth**: JWT required
- **Service**: `WebsocketPresenceHandler`
- **Tables**: `presence` (in-memory or cache)
- **Request**: none
- **Response**: `List<PlayerPresenceData>` via JSON wrapper

---

### GET `presence/{userId}`

- **Auth**: JWT required
- **Service**: `WebsocketPresenceHandler`
- **Tables**: `presence`
- **Request**: none (userId in URL)
- **Response**: `PlayerPresenceData`

---

## Global / Admin

### GET `auth/global/global-message/current`

- **Auth**: JWT required
- **Service**: `WebsocketGlobalHandler.GetCurrentAsync` / `FetchCurrentAsync`
- **Tables**: `global_messages` (or in-memory)
- **Request**: none
- **Response**:
  ```json
  { "ok": true, "data": { "title": "string", "text": "string", "remainingSeconds": 3600, "durationSeconds": 7200 } }
  ```

---

### GET `auth/global/active-map-events`

- **Auth**: JWT required
- **Service**: `WebsocketGMEventsHandler.GetActiveEventsAsync`
- **Tables**: `map_events`
- **Request**: none
- **Response**:
  ```json
  { "ok": true, "data": [ { "eventId": 1, "mapId": 1, "name": "string", "description": "string", "remainingSeconds": 3600, "endsAt": "date" } ] }
  ```

---

### GET `auth/role/me`

- **Auth**: JWT required
- **Service**: `WebsocketGlobalHandler.IsSupportOrGmAsync`
- **Tables**: `users`
- **Request**: none
- **Response**:
  ```json
  { "ok": true, "data": { "accountType": "GM" } }
  ```

---

### POST `auth/gm/announce`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGlobalHandler.SetAsync`
- **Tables**: `global_messages`
- **Request**:
  ```json
  { "title": "string", "body": "string", "duration": 3600, "endsSeconds": 7200 }
  ```
- **Response**: raw string

---

### DELETE `auth/gm/global-message`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGlobalHandler.ClearAsync`
- **Tables**: `global_messages`
- **Request**: none
- **Response**: raw string

---

### POST `auth/gm/map-event/start`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGMEventsHandler.StartMapEventAsync`
- **Tables**: `map_events`
- **Request**:
  ```json
  { "mapId": 1, "eventId": 1, "durationSeconds": 7200, "name": "string", "description": "string" }
  ```
- **Response**: raw string

---

### POST `auth/gm/map-event/stop-all`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGMEventsHandler.StopAllMapEventsAsync`
- **Tables**: `map_events`
- **Request**: no body
- **Response**: raw string

---

### POST `auth/gm/mail/send`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGMGiftsHandler.SendMailAsync`
- **Tables**: `mail_inbox`, `mail_messages`
- **Request**:
  ```json
  { "audience": "specific", "targetUserId": 1, "title": "string", "body": "string", "attachments": [ { "type": "Currency", "id": "GOLD", "amount": 100 } ], "requiresConfirm": false, "deliverStart": "date", "deliverEnd": "date", "expiresAt": "date" }
  ```
- **Response**: raw JSON containing `"ok":true`

---

### GET `auth/gm/player/profile?nickname={urlEncoded}`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGMPlayerHandler.FindByNicknameAsync`
- **Tables**: `users`, `profiles`
- **Request**: none (query param)
- **Response**:
  ```json
  { "ok": true, "data": { "userId": 1, "displayName": "string", "iconId": "string", "frameId": "string", "favouriteCharacterId": 1, "isOnline": true, "currentRoomId": "string", "currentRoomType": "string", "rank": { "rank": 42, "score": 1000 }, "account": { "banned": false, "status": "active", "banReason": null, "bannedUntil": null } }, "error": null }
  ```

---

### POST `auth/gm/ban`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGMPlayerHandler.BanAsync`
- **Tables**: `users`
- **Request**:
  ```json
  { "targetUserId": 1, "permanent": false, "reason": "string", "until": "date" }
  ```
- **Response**: raw JSON containing `"ok":true`

---

### POST `auth/gm/unban`

- **Auth**: JWT required (GM role)
- **Service**: `WebsocketGMPlayerHandler.UnbanAsync`
- **Tables**: `users`
- **Request**:
  ```json
  { "targetUserId": 1 }
  ```
- **Response**: raw JSON containing `"ok":true`
