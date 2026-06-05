# Account/Profile System

> **Status**: In Design
> **Design Order**: #18 (MVP)
> **Category**: Persistence
> **Layer**: Core
> **Implements Pillar**: P3 (Snappy Sessions — fast login, seamless profile load)
> **Depends On**: Network Manager (#4), Save/Profile Persistence (#10)
> **Depended On By**: (none)

---

## 1. Overview

The Account/Profile System manages the player's identity and persistent progression data across sessions. On first launch, it guides the player through account creation (email/username + password via WebSocket backend); on subsequent launches, it authenticates the player, fetches their profile from the server, and populates local state so the game knows who the player is, what they own, and where they left off. The system wraps the template's `IBackendService` auth endpoints (`/auth/register`, `/auth/login`, `/profile/get`) and coordinates with Save/Profile to hydrate local state after login. It also owns session token management — storing the auth token for reconnection without re-entering credentials. The player experiences this system as the confidence that their progress is theirs: same account, same profile, same story, on any device.

---

## 2. Player Fantasy

**Account creation** (one-shot): The player types their credentials into a rune-etched interface. Each character lights up like an ancient inscription bonding the player to the Rift. On completion, a single pulse of recognition — then the camp loads. The auth call runs *behind* the animation; the player never waits on a spinner for their one-time sign-up.

**Every login after** (invisible): The player launches the game and lands in Hero Camp. No login screen, no "Connecting..." spinner. The token authenticates in under 500ms; the camp is already warm. The player's currency, unlocks, and lore are where they left them. They feel *expected* — the Rift remembered them.

**Offline grace**: If the backend is slow, the camp loads in cached-offline mode with a subtle "Rift stabilizing..." badge. The player can browse the Codex, inspect their build, or change settings while the connection resolves in the background. No blank spinner. No forced re-auth mid-session.

**P3 delivery**: Account creation has ceremony (it happens once). Login is zero-friction (it happens every session). Token refresh is silent and deferred. The fantasy is "my game, my space, ready when I am."

---

## 3. Detailed Rules

### 3.1 Core Principles

1. **Thin facade over template auth** — The Account/Profile System is a thin `LoginService` facade over the template's built-in `WebsocketAuthHandler`. The template already handles register, login, guest, auto-login cascade, and logout with `SecurePrefs`-based token storage. The new code wraps these into a game-specific interface — it does not reimplement auth from scratch.

2. **Offline mode skips auth entirely** — When `BackendSettings.BackendMode == Offline`, no auth calls occur. The player boots directly into the game with a local-only profile. `OfflineBackendService` provides all backend responses locally.

3. **Connection readiness gate** — All auth operations must await `INetworkManager.ConnectionState == Connected` before executing. If connection fails, auth errors surface directly (no silent offline fallback for auth — offline fallback is for gameplay continuity, not auth bypass).

### 3.2 Account Creation Flow

1. Player enters email/username + password (+ confirm password) on the account creation screen.
2. Client validates: email format (regex), password minimum length (8 characters).
3. Calls `POST /auth/register` via `WebsocketAuthHandler.RegisterAsync(email, password, confirmPass)`.
4. Server atomically creates rows in `users`, `profiles`, and `currencies` tables (transaction).
5. On success: server returns a JWT session token and initial `PersistentSaveData` (gold=0, premium=0, no unlocks).
6. Client stores credentials and token via `SecurePrefs.SetEncryptedStringToFile()`.
7. Client hydrates local Save/Profile with the returned persistent data.
8. On failure: server returns a standardized error code (`EMAIL_TAKEN`, `WEAK_PASSWORD`, `INVALID_EMAIL`, `SERVER_ERROR`). Client displays the error inline on the registration form.

### 3.3 Login Flow

1. **Auto-login (cold start)**: On app launch, `WebsocketAuthHandler.TryAutoLoginAsync()` runs:
   - Reads saved JWT from `SecurePrefs` (stored at `persistentDataPath/secure_prefs.json` — AES-128-CBC + HMAC-SHA-256).
   - Validates JWT via lightweight `GET /auth/me` (signature + expiry check — no DB lookup).
   - If valid: login complete. Client hydrates local state.
   - If expired: falls back to `POST /auth/login` with cached email/password from SecurePrefs.
   - If credentials missing: shows login screen.
   - **Cached-first UI**: `Save/Profile.LoadPersistentAsync()` runs first, so cached profile data populates the camp immediately. `auth/me` validation runs in background. If validation fails, the login screen replaces the cached camp gracefully.
2. **Manual login**: Player enters credentials on login screen. Calls `POST /auth/login`. On success, stores token + credentials via `SecurePrefs`. On failure, displays error (standardized codes: `INVALID_CREDENTIALS`, `ACCOUNT_LOCKED`, `SERVER_ERROR`).

### 3.4 Profile Fetch and Hydration

1. After successful login/register, calls `GET /auth/init` (not `/profile/get` — the init endpoint returns profile, currencies, `charactersData`, owned items, progress, rewards, used coupons, and claimed map rewards in a single response).
2. The `LoginService` acts as the **init-data coordinator**: it receives the multi-domain `auth/init` response and dispatches each domain to the owning system:
   - Currency data → Currency System
   - Profile data → Save/Profile (`PersistentSaveData`)
   - Character data → Character System (future)
   - Inventory data → Inventory System (future)
3. **Ordering guarantee**: `LoadPersistentAsync()` completes **before** auto-login begins. This ensures cached state is available for immediate UI, and `auth/init` data cleanly overwrites it.
4. **Server data always wins** on init. Local dirty writes queue until after init completes.

### 3.5 Session Token Management

1. Tokens are stored via `SecurePrefs.SetEncryptedStringToFile()` — AES-128-CBC + HMAC-SHA-256, written to `persistentDataPath/secure_prefs.json`.
2. Stored keys: `colyseus_jwt` (session token), `colyseus_uid` (player ID), `colyseus_email`, `colyseus_pass`.
3. Token survives app restart (persistentDataPath persists). Does not survive app reinstall (OS wipes sandbox) — player must re-authenticate.
4. **Token refresh**: MVP uses the template's auto-login cascade (re-login with cached credentials) rather than a dedicated `POST /auth/refresh` endpoint. No true refresh token exists in MVP. If template server-side session invalidation exists, it is used on logout; otherwise logout is client-only (tokens expire naturally).
5. Mid-session token expiry is handled by queuing sync operations and silently re-authenticating via the cascade before the next write. Player is never prompted for credentials mid-session.

### 3.6 Logout

1. Calls `WebsocketAuthHandler.LogOut()` — client-only: clears SecurePrefs keys (JWT, email, password) and nulls the in-memory token.
2. Server-side logout (invalidate JWT or session) is confirmed by checking `BackendManager.Service?.Logout()`. If the template implements this, it runs; if not, tokens expire naturally.
3. Returns the player to the login screen.
4. No auth call is made during logout — purely local operation.

### 3.7 Auth State Machine

The system does not own a formal auth FSM for MVP. The template's `WebsocketAuthHandler` cascade strategy (try JWT → try email/pass → try guest → fail) replaces the need for a state machine with logged states. The only game-facing auth states are:

| State | Meaning | UI Response |
|-------|---------|-------------|
| `Uninitialized` | No profile loaded yet | Show loading screen |
| `LoggedIn` | Authenticated, profile loaded | Show camp/gameplay |
| `LoggedOut` | Not authenticated, no valid credentials | Show login screen |
| `AuthFailed` | Credentials rejected, rate-limited, or backend error | Show login screen with error message |

These are derived from the Network Manager's connection FSM + cached profile presence. If no cached profile exists and connection fails, show login with error. No separate auth FSM class is needed for MVP.

### 3.8 Password Policy

- Minimum length: 8 characters.
- Client-side validation mirrors server-side rules (email regex, password length).
- Server enforces all policies authoritatively. Client validation is UX convenience, not security.
- `IBackendService.AccountRegister` accepts a `confirmPass` parameter — client must send the confirmed password; mismatch is caught client-side before the server call.

### 3.9 Server-Side Init Contract

When a new account is registered, the server must atomically create:

| Table | Initial State |
|-------|--------------|
| `users` | `{ email, username, password_hash, last_login = NOW(), guestPass = null }` |
| `profiles` | `{ player_id, gold = 0, premium_currency = 0, unlocked_hero_ids = [], unlocked_zone_ids = [] }` |
| `currencies` | `{ player_id, total_earned_gold = 0, total_spent_gold = 0, ... }` |

`last_login` is updated server-side on every successful login/auto-login (not client-side).

### 3.10 Error Code Contract

Auth endpoints return standardized error codes:

| HTTP Status | Error Code | Meaning |
|-------------|-----------|---------|
| 200 | — | Success |
| 400 | `INVALID_EMAIL` | Email format rejected |
| 400 | `WEAK_PASSWORD` | Password below minimum length |
| 400 | `EMAIL_TAKEN` | Email already registered |
| 401 | `INVALID_CREDENTIALS` | Email/password mismatch |
| 401 | `ACCOUNT_LOCKED` | Rate-limited or admin-locked |
| 429 | `RATE_LIMITED` | Too many login attempts |
| 5xx | `SERVER_ERROR` | Internal server error (not a credential issue) |

The client must distinguish HTTP 400/401 from 500 to avoid mislabeling server errors as credential failures. The template's generic `"invalid_credentials"` catch for all HTTP errors must be replaced with error-code-aware handling.

---

## 4. Formulas

None. The Account/Profile System is an orchestration layer with no mathematical calculations. Rate limits and JWT expiry are server-configured, not system formulas.

---

## 5. Edge Cases

- **If registration returns `EMAIL_TAKEN`**: Display inline error on the registration form below the email field. Player can edit and resubmit. No state loss.

- **If login returns `INVALID_CREDENTIALS`**: Display "Incorrect email or password" on the login form. Do not reveal whether the email exists (security best practice).

- **If login returns `ACCOUNT_LOCKED`**: Display "Account temporarily locked — try again later" with a suggested wait time if the server provides one.

- **If login returns `RATE_LIMITED`**: Display "Too many login attempts. Please wait a few minutes." Disable the submit button for 60 seconds (client-side cooldown).

- **If the backend returns HTTP 5xx during auth**: Display "Server error — please try again." Differentiate from credential errors. Do NOT show "invalid credentials" (the template's default catch-all is overridden by the error code contract in Section 3.10).

- **If the backend is unreachable during login** (timeout, DNS failure): Display "Could not connect to server. Check your internet connection." Do not silently fall back to offline mode — offline fallback is for gameplay continuity, not auth bypass.

- **If the player launches the game while offline** (no internet): Show login screen with a "Connect to the internet to sign in" message. If a cached profile exists, show the Hero Camp in cached-offline mode with "Reconnecting..." badge instead.

- **If the JWT token expires mid-session**: Queue pending sync operations locally. On the next sync attempt, detect 401 response and silently re-authenticate via the auto-login cascade (try JWT → try cached email/pass). If re-auth succeeds, replay queued syncs. If re-auth fails, surface a "Session expired — please log in" modal on the next UI transition point (camp entry, not mid-combat).

- **If `auth/me` returns 401 during auto-login** (saved JWT expired): Fall back to `POST /auth/login` with cached credentials from SecurePrefs. If that also fails, the login screen appears — the player must re-enter credentials.

- **If the app is reinstalled** (SecurePrefs wiped): No cached credentials exist. `TryAutoLoginAsync()` immediately transitions to the login screen. No error — this is expected behavior.

- **If the player is already logged in and calls register or login again**: The client should not present these options when already logged in. Guard: if `AuthState == LoggedIn`, hide login/register screens from navigation. If the call is made programmatically in error, return success immediately (no-op).

- **If `LoadPersistentAsync()` has not completed when auto-login finishes**: The init coordinator awaits Save/Profile's ready signal before writing hydrated data. Under normal flow, `LoadPersistentAsync()` completes before auto-login begins (Section 3.4 Rule 3). This edge case only occurs if Save/Profile initialization is unexpectedly delayed. Remedy: `auth/init` data is queued until Save/Profile signals readiness.

- **If offline mode is enabled but SecurePrefs has stale credentials**: Ignored. Offline mode skips all auth calls. Stale credentials are harmless — SecurePrefs is simply never read for auth purposes.

- **If the same account is used on two devices**: Handled by server-authoritative economy (Save/Profile GDD, Rule 7): per-device earnings credits, minimum 15-min sync interval, rolling cap 50,000 gold/24h. Account/Profile does not need additional rules — after login, profile fetch returns the merged authoritative state.

- **If registering a new account fails halfway** (server creates user row but crashes before profile/currency): The register endpoint must use a server-side transaction. If the transaction fails, the database is rolled back — no orphan rows. This is a server-side requirement, not client-handled.

---

## 6. Dependencies

### Hard Dependencies

| System | # | Nature of Dependency |
|--------|---|----------------------|
| Network Manager | 4 | Provides `IsConnected` gate for all auth calls. Connection readiness must be `Connected` before auth operations execute. |
| Save/Profile Persistence | 10 | Reads/writes `PersistentSaveData` for profile hydration. `LoadPersistentAsync()` must complete before auto-login. |
| Backend Transport (template) | — | `IBackendService` via `WebSocketSqlBackendService` (online) or `OfflineBackendService` (offline). The template's `WebsocketAuthHandler` provides register/login/auto-login/logout. |

### Soft Dependencies

| System | # | Nature of Dependency |
|--------|---|----------------------|
| Currency System | 16 | Receives currency data from `auth/init` fan-out after login. No direct coupling — data flows through `LoginService` coordinator. |
| HUD / Login UI | 30 | Consumes auth state for login screen display. `LoginService` exposes `AuthState` for UI binding. |

### Bidirectional Consistency

- Network Manager lists "Account/Profile — Checks `IsConnected` before login call" (✓ matches this GDD)
- Save/Profile lists "Account/Profile — Reads profile data after login to populate initial state" (✓ matches this GDD)

---

## 7. Tuning Knobs

| Knob | Default | Range | Affects | Owner |
|------|---------|-------|---------|-------|
| JWT session token duration | 24h | 1–168h | How long a token is valid before re-auth is needed | Server |
| Login rate limit (attempts per minute) | 5 | 2–20 | Max failed attempts before `ACCOUNT_LOCKED` | Server |
| Rate limit cooldown | 60s | 30–600s | Lockout duration | Server |
| Password minimum length | 8 | 6–20 | Server-enforced minimum | Server |
| Cached profile staleness threshold | 7d | 1–30d | Max age of local cached profile before forcing online login | Client |

All knobs are server-configured except "cached profile staleness threshold" which is client-side.

---

## 8. Acceptance Criteria

### Registration

- **AC1** — **GIVEN** the player enters a valid email `"test@example.com"` and password `"password123"` with matching confirm password, **WHEN** `RegisterAsync` is called AND `Network.IsConnected == true`, **THEN** the mock server received `POST /auth/register` with `{email, password, confirmPass}` AND the response contains a `token` AND `colyseus_jwt`, `colyseus_email`, `colyseus_pass` are written to SecurePrefs.

- **AC2** — **GIVEN** the player enters an already-registered email `"taken@example.com"`, **WHEN** `RegisterAsync` is called, **THEN** the response error code is `EMAIL_TAKEN` AND the registration form shows the error inline AND SecurePrefs values are unchanged AND `AuthState` remains `LoggedOut`.

- **AC3** — **GIVEN** the player enters a password of 6 characters (below 8 minimum), **WHEN** the client validates, **THEN** the register button is disabled AND a hint "minimum 8 characters" is shown AND no server call is made.

- **AC4** — **GIVEN** the player enters a valid email but mismatched confirm password, **WHEN** the client validates, **THEN** a "passwords do not match" hint is shown AND no server call is made.

### Login

- **AC5** — **GIVEN** the player enters valid credentials for an existing account, **WHEN** `LoginAsync` is called AND `Network.IsConnected == true`, **THEN** the response contains a `token` AND `colyseus_jwt`, `colyseus_email`, `colyseus_pass` are written to SecurePrefs AND `AuthState` transitions to `LoggedIn`.

- **AC6** — **GIVEN** the player enters incorrect credentials, **WHEN** `LoginAsync` is called, **THEN** the response error code is `INVALID_CREDENTIALS` AND the login form shows "Incorrect email or password" AND SecurePrefs is unchanged AND `AuthState` remains `LoggedOut`.

- **AC7** — **GIVEN** the server returns HTTP 401 with error code `ACCOUNT_LOCKED`, **WHEN** `LoginAsync` is called, **THEN** the login form shows "Account temporarily locked — try again later".

- **AC8** — **GIVEN** the server returns HTTP 429 with error code `RATE_LIMITED`, **WHEN** `LoginAsync` is called, **THEN** the login button is disabled for 60 seconds AND a cooldown message is displayed AND the timer survives scene transitions (app minimized, scene change).

- **AC9** — **GIVEN** the server returns HTTP 500 during login, **WHEN** the response is received, **THEN** the client displays "Server error — please try again" AND does NOT display "invalid credentials" (verifies error code differentiation between 4xx and 5xx).

- **AC10** — **GIVEN** the backend is unreachable (timeout, DNS failure) during login, **WHEN** the connection fails, **THEN** the client displays "Could not connect to server. Check your internet connection." AND does NOT silently switch to offline mode.

### Auto-Login

- **AC11** — **GIVEN** SecurePrefs has a valid `colyseus_jwt` AND `GET /auth/me` returns 200, **WHEN** `TryAutoLoginAsync` runs at app start, **THEN** `AuthState` reaches `LoggedIn` AND no login screen is shown AND `LoadPersistentAsync()` completed before `auth/init` data was written.

- **AC12** — **GIVEN** SecurePrefs has an expired JWT (`auth/me` returns 401) AND valid `colyseus_email`/`colyseus_pass`, **WHEN** `TryAutoLoginAsync` runs, **THEN** the cascade calls `POST /auth/login` with cached credentials AND `AuthState` reaches `LoggedIn`.

- **AC13** — **GIVEN** SecurePrefs has no saved credentials (fresh install), **WHEN** `TryAutoLoginAsync` runs, **THEN** `AuthState` reaches `LoggedOut` AND the login screen is displayed AND no error message is shown (this is expected).

### Logout

- **AC14** — **GIVEN** the player is logged in (`AuthState == LoggedIn`), **WHEN** `LogOut()` is called, **THEN** `colyseus_jwt`, `colyseus_uid`, `colyseus_email`, and `colyseus_pass` are removed from SecurePrefs AND `AuthState` transitions to `LoggedOut` AND the login screen is displayed.

### Offline Mode

- **AC15** — **GIVEN** `BackendSettings.BackendMode == Offline`, **WHEN** the game boots, **THEN** no auth calls are made AND the player reaches the game directly (no login screen) AND `AuthState` is derivable as `LoggedIn`.

### Connection Gate

- **AC16** — **GIVEN** `Network.IsConnected == false`, **WHEN** `RegisterAsync` or `LoginAsync` is called, **THEN** the call is deferred until `Network.IsConnected == true` (observed via `OnStateChanged` event) AND the call executes only after connection is established.

### Mid-Session Token Expiry

- **AC17** — **GIVEN** the JWT expires mid-session AND a sync operation triggers a 401 response AND the auto-login cascade succeeds (re-auth via cached credentials), **WHEN** re-authentication completes, **THEN** the queued sync operation is replayed AND no modal or prompt is shown to the player.

- **AC18** — **GIVEN** the JWT expires mid-session AND the auto-login cascade fails (both JWT and cached credentials rejected), **WHEN** the next UI transition point is reached (camp entry, not mid-combat), **THEN** a "Session expired — please log in" modal is shown AND the player must re-enter credentials.

### Cached Profile Staleness

- **AC19** — **GIVEN** the local cached `persistent.json` is older than 7 days (staleness threshold), **WHEN** `TryAutoLoginAsync` completes, **THEN** the login screen is shown (player must re-authenticate online) even if SecurePrefs has valid credentials.

### Already-Logged-In Guard

- **AC20** — **GIVEN** `AuthState == LoggedIn`, **WHEN** the player navigates to the login or register screen, **THEN** the screen is not shown (redirect to camp). **WHEN** `RegisterAsync` or `LoginAsync` is called programmatically, **THEN** the call returns success immediately (no-op).
