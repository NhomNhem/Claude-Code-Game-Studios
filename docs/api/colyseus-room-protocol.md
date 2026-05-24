# Colyseus Room Protocol — Tiny Rift Survivors

The backend uses Colyseus WebSocket rooms for realtime features.
Two rooms are defined: `presence_room` and `friends_room`.
All HTTP REST is handled by the Colyseus HTTP client (see `rest-api-map.md`).

---

## Room: `presence_room`

### Class
`PresenceRoom` (server-side name: `"presence_room"`)
Client: `WebsocketPresenceHandler.cs`

### Join / Create
`client.JoinOrCreate<PresenceRoomState>("presence_room", joinOptions)`

**joinOptions:**
```json
{ "userId": 1, "username": "string" }
```

### State Schema (`PresenceRoomState`)

| # | Type | Name | Description |
|---|------|------|-------------|
| 0 | `MapSchema<PlayerPresenceSchema>` | `players` | Keyed by userId string |

**`PlayerPresenceSchema`:**

| # | Type | Name | Description |
|---|------|------|-------------|
| 0 | `string` | `userId` | Player's user ID |
| 1 | `string` | `username` | Display name |
| 2 | `boolean` | `isOnline` | Online status |
| 3 | `number` | `lastOnline` | Last online timestamp (epoch ms) |
| 4 | `number` | `lastLogin` | Last login timestamp (epoch ms) |
| 5 | `number` | `totalOnlineSeconds` | Cumulative online time |
| 6 | `string` | `currentRoomId` | Current game room (if in match) |
| 7 | `string` | `currentRoomType` | Room type descriptor, format: `"{type}\|{mapName}"` |
| 8 | `number` | `unreadMailCount` | Unread mail count for badge |

### Client → Server Messages

#### `"heartbeat"`

Sent every 30 seconds from the client.

**Payload:**
```json
{ "ts": 637900000000000000 }
```
(ticks = `DateTime.UtcNow.Ticks`)

**Purpose:** Keep presence alive, update `lastOnline`/`totalOnlineSeconds` on server.

---

#### `"set_room"`

Sent when player enters a game room (match, arena, etc.).

**Payload:**
```json
{ "roomId": "string", "roomType": "string" }
```

**Effect:** Updates `currentRoomId` and `currentRoomType` in the player's presence state.
`roomType` convention: `"{type}|{mapName}"` (e.g. `"match|arena1"`).

---

#### `"clear_room"`

Sent when player leaves a game room.

**Payload:**
```json
{}
```

**Effect:** Clears `currentRoomId` and `currentRoomType`.

---

#### `"invite_coop"`

Sent when inviting another player to a co-op session.

**Payload:**
```json
{ "toUserId": "2", "roomId": "string", "mapName": "string", "capacity": 2 }
```

**Effect:** Server routes invite to target user's client.

---

### Server → Client Messages

#### `"invite_coop"`

**Payload shape:** `CoopInvitePayload`
```json
{ "fromUserId": "string", "fromUsername": "string", "roomId": "string", "mapName": "string", "capacity": 2 }
```

**Client handler:** `Presence_OnCoopInvite` event → forwarded to UI as `IBackendService.Presence_OnCoopInvite`.

---

#### `"global_announce"`

**Payload shape:** `GlobalAnnounceWire`
```json
{ "title": "string", "text": "string", "durationSeconds": 3600 }
```

**Client handler:** `OnGlobalMessage(text, durationSeconds)` → shows global announcement banner.

---

#### `"global_message_clear"`

**Payload:** no body

**Client handler:** `OnGlobalMessageClear` → hides announcement banner.

---

#### `"map_event_start"`

**Payload shape:** `MapEventStartedPayload`
```json
{ "eventId": 1, "mapId": 1, "name": "string", "description": "string", "durationSeconds": 7200 }
```

**Client handler:** `OnMapEventStart` → triggers map event UI.

---

#### `"map_event_stop_all"`

**Payload:** no body

**Client handler:** `OnMapEventsStopAll` → removes all map event indicators.

---

#### `"mail_badge"`

**Payload shape:** `MailBadgePayload`
```json
{ "unread": 5 }
```

**Client handler:** `OnMailBadge(unread)` — updates mail icon badge count.

---

## Room: `friends_room`

### Class
`FriendsRoom` (server-side name: `"friends_room"`)
Client: `WebsocketFriendsHandler.cs`

### Join / Create
`client.JoinOrCreate<FriendsRoomState>("friends_room", joinOptions)`

**joinOptions:**
```json
{ "userId": 1 }
```

### State Schema (`FriendsRoomState`)

| # | Type | Name | Description |
|---|------|------|-------------|
| 0 | `MapSchema<FriendEntrySchema>` | `friends` | Keyed by friend userId string |

**`FriendEntrySchema`:**

| # | Type | Name | Description |
|---|------|------|-------------|
| 0 | `number` | `userId` | Friend's user ID |
| 1 | `string` | `displayName` | Friend's display name |
| 2 | `string` | `iconId` | Friend's avatar icon ID |
| 3 | `string` | `frameId` | Friend's avatar frame ID |
| 4 | `number` | `favouriteCharacterId` | Friend's favourite character |
| 5 | `boolean` | `isOnline` | Friend's online status |
| 6 | `string` | `currentRoomId` | Friend's current room (if in game) |
| 7 | `string` | `currentRoomType` | Friend's room type descriptor |

### Client → Server Messages

#### `"remove"`

Sent when removing a friend (also uses REST `POST auth/friends/remove`).

**Payload:**
```json
{ "friendUserId": 2 }
```

**Effect:** Removes friend from both sides in realtime.

### Server → Client Messages

#### `"pending"`

**Payload shape:** `FriendPendingPayload`
```json
{ "incoming": [ 1, 2 ], "outgoing": [ 3 ] }
```
(user ID arrays for pending friend requests)

**Client handler:** Updates local `_incoming`/`_outgoing` pending sets, raises `OnPendingChanged` event.

---

## Related Services & Database Tables

| Room | Service Class | Tables Touched | Unity Features |
|------|--------------|----------------|----------------|
| `presence_room` | `WebsocketPresenceHandler` | `presence` (in-memory/cache), `profiles` (online status) | Friend list online indicator, player profile card, coop invite modal |
| `friends_room` | `WebsocketFriendsHandler` | `friends`, `friend_requests`, `blocked_users` | Friends list, pending requests, friend presence in lobby |
