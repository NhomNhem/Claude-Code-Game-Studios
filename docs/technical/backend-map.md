# Backend Map — Tiny Rift Survivors

## Architecture Decision

**WebSocket + SQL is the primary production backend from day one.**
Offline mode is dev/test/fallback only.
Firebase is deferred and not part of the primary path.

## Backend Roles

| Backend | Role | Status |
|---------|------|--------|
| WebSocket + SQL | Primary production backend | M0 |
| Offline | Dev/test/fallback (local-only) | M0 (built in template) |
| Firebase | Deferred — not part of primary path | Not planned |

## Template's Built-In Backend Layer

The BulletHell Elemental Template already provides the full abstraction via
`IBackendService` and `BackendLifetimeScope` (VContainer):

```
IBackendService (interface)
├── WebSocketSqlBackendService   ← PRIMARY — configure for production
├── OfflineBackendService        ← FALLBACK — dev/test, local persistence
└── FirebaseBackendService       ← DEFERRED — do not initialize
```

All three are already implemented. We configure and extend, not rebuild.

## M0 Deliverables

### Unity Side (Assets/_TinyRift/)

```
Assets/_TinyRift/
└── Scripts/
    └── Backend/
        ├── BackendSettings.asset          # ScriptableObject — toggle Online/Offline/Mock
        ├── BackendBootstrap.cs            # VContainer registration + startup init
        ├── WebSocketConfig.cs             # URL, port, reconnect settings
        ├── LoginService.cs                # Login/register flow
        ├── ProfileService.cs              # Player profile data
        ├── CurrencyService.cs             # Server-authoritative currency
        └── MessageHandler.cs              # Server message routing
```

#### BackendSettings.asset (ScriptableObject)
```
- backendMode: Online | Offline | Mock
- serverUrl: "ws://localhost:8080"
- reconnectAttempts: 5
- autoReconnect: true
- offlineFallbackOnDisconnect: true
```

#### BackendBootstrap
```
- Registered in VContainer at game startup
- Reads BackendSettings.asset
- Initializes the appropriate IBackendService implementation
- For Online mode: starts WebSocket connection, authenticates
- For Offline mode: uses OfflineBackendService (local PlayerSave)
```

### Server Side (tiny-rift-server — separate repo)

```
tiny-rift-server/
├── package.json                 # Node.js project
├── src/
│   ├── index.ts                 # Entry point, Colyseus server
│   ├── config.ts                # Server config
│   ├── database/
│   │   ├── connection.ts        # MySQL connection pool
│   │   └── schema.sql           # DDL for all tables
│   ├── handlers/
│   │   ├── auth.ts              # Login/register handler
│   │   ├── profile.ts           # Profile read/write
│   │   └── currency.ts          # Server-authoritative currency ops
│   └── middleware/
│       └── auth.ts              # Token validation
└── schema.sql                   # MySQL schema (canonical)
```

### MySQL Schema (MVP)

```sql
-- Users & Auth
users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP NULL
)

-- Player Profiles
profiles (
  id BIGINT UNSIGNED PRIMARY KEY,   -- FK → users.id
  display_name VARCHAR(32) NOT NULL,
  avatar_id INT DEFAULT 0,
  total_play_time BIGINT DEFAULT 0,
  games_played INT DEFAULT 0,
  highest_wave INT DEFAULT 0,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)

-- Server-Authoritative Currency
currencies (
  id BIGINT UNSIGNED PRIMARY KEY,   -- FK → users.id
  gold BIGINT DEFAULT 0,
  gems INT DEFAULT 0,
  total_gold_earned BIGINT DEFAULT 0,
  total_gem_earned INT DEFAULT 0,
  version INT DEFAULT 1,            -- Optimistic concurrency
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)

-- Leaderboards (future)
leaderboard_entries (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED NOT NULL,
  wave INT NOT NULL,
  score BIGINT NOT NULL,
  character_used VARCHAR(32),
  achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### End-to-End Flow (MVP)

```
Unity Startup
  │
  ├── BackendBootstrap.Awake()
  │     └── Read BackendSettings.asset → mode = Online
  │
  ├── VContainer.Register(WebSocketSqlBackendService)
  │
  ├── Connect("ws://localhost:8080")
  │     │
  │     └── Server: accept, request auth
  │
  ├── Login(username, password)
  │     │
  │     └── Server: validate credentials, return { token, user, profile, currency }
  │
  ├── ProfileService.Load()
  │     └── Display player info in Home scene
  │
  └── CurrencyService.GetBalance()
        └── Show gold/gems in HUD and menus
```

## Define Symbols

| Build | Defines | IBackendService |
|-------|---------|-----------------|
| Production | `UNITY_PIPELINE_URP` | WebSocketSqlBackendService |
| Dev/Editor | `UNITY_PIPELINE_URP` | Per BackendSettings.asset |
| Offline dev | `UNITY_PIPELINE_URP` | OfflineBackendService |

No `FIREBASE` define on any platform. Remove from Player Settings.
No `FUSION_*` defines on any platform. Remove from Player Settings.

## Security

- Server-side: password hashing (bcrypt), session tokens (JWT), rate limiting
- Unity client: store token in SecurePrefs (already exists in template)
- Server-authoritative: all currency/score operations validated server-side
- No sensitive data in client memory after logout
- SQL injection protection via parameterized queries (server-side only)
