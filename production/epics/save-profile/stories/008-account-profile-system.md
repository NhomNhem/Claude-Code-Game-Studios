# Story 008: Account/Profile System

- **Epic**: Save & Profile
- **System**: Account/Profile System
- **Type**: Integration
- **Priority**: P0
- **Estimate**: 4h
- **Status**: Ready
- **Last Updated**: 2026-06-02

## GDD Requirements

| TR-ID | Requirement | Status |
|-------|-------------|--------|
| `TR-account-001` | Login/registration via WebSocketSQL backend | ✅ ADR-001 |
| `TR-account-002` | Profile fetch/update via WebSocketSQL backend | ✅ ADR-001 |
| `TR-account-003` | Profile data after login populates initial state | ✅ ADR-001 |

## ADR Guidance

**ADR-001 (VContainer DI Architecture):**
- `ILoginService` interface singleton in `TinyRiftScope`
- Wraps template's `WebsocketAuthHandler` — thin facade, not reimplementation
- Coordinates with `IPersistStateService` for profile hydration after auth

**Control Manifest (Core Layer):**
- Offline mode (`BackendSettings.BackendMode == Offline`) skips auth entirely
- Connection readiness gate: await `INetworkManager.ConnectionState == Connected`
- Profile hydration via `auth/init` fan-out to owning systems

## Description

Implement the Account/Profile System: login/registration via WebSocketSQL backend (thin facade over template's `WebsocketAuthHandler`), session token storage in SecurePrefs, and profile hydration after authentication.

## Design

### LoginService API

```csharp
public interface ILoginService
{
    AuthState CurrentAuthState { get; }
    UniTask<AuthResult> RegisterAsync(string email, string password, string confirmPass);
    UniTask<AuthResult> LoginAsync(string email, string password);
    UniTask TryAutoLoginAsync();
    void LogOut();
}

public enum AuthState { Uninitialized, LoggedIn, LoggedOut, AuthFailed }
```

### Registration Flow

1. Client validates: email format (regex), password >= 8 chars, passwords match
2. Caches credentials in SecurePrefs
3. Calls `POST /auth/register` via `WebsocketAuthHandler.RegisterAsync()`
4. Server atomically creates `users`, `profiles`, `currencies` rows (transaction)
5. On success: stores JWT in SecurePrefs, transitions to LoggedIn, fetches profile
6. On failure: returns standardized error code, stays LoggedOut

### Login Flow

1. **Auto-login**: On cold start, `WebsocketAuthHandler.TryAutoLoginAsync()` runs:
   - Reads JWT from SecurePrefs
   - Validates via `GET /auth/me`
   - If valid: LoggedIn, fetch profile
   - If expired: cascade to `POST /auth/login` with cached credentials
   - If no credentials: show login screen (LoggedOut)
2. **Manual login**: Player enters credentials, calls `POST /auth/login`
3. Cached-first UI: `LoadPersistentAsync()` completes before auto-login begins

### Profile Hydration

After successful login:
1. Call `GET /auth/init` (returns profile, currencies, inventory, progress in one response)
2. `LoginService` acts as init-data coordinator — dispatches each domain:
   - Currency data → Currency System
   - Profile data → Save/Profile (`PersistentSaveData`)
   - Character data → Character System (future)
   - Inventory → Inventory System (future)
3. Ordering guarantee: `LoadPersistentAsync()` completes before auto-login begins

### Session Token Management

- Tokens stored via `SecurePrefs.SetEncryptedStringToFile()` (AES-128-CBC + HMAC-SHA-256)
- Stored keys: `colyseus_jwt`, `colyseus_uid`, `colyseus_email`, `colyseus_pass`
- Token survives app restart, not reinstall

### Logout

- Calls `WebsocketAuthHandler.LogOut()` — clears SecurePrefs, nulls in-memory token
- Pure local operation, no server call
- Returns to login screen

## Acceptance Criteria

1. **GIVEN** valid email `"test@example.com"` and password `"password123"` with matching confirm, **WHEN** `RegisterAsync` is called AND `Network.IsConnected == true`, **THEN** server receives `POST /auth/register` AND response contains a `token` AND SecurePrefs stores the credentials.
2. **GIVEN** an already-registered email, **WHEN** `RegisterAsync` is called, **THEN** error code `EMAIL_TAKEN` is returned AND SecurePrefs unchanged AND `AuthState` remains `LoggedOut`.
3. **GIVEN** valid credentials for an existing account, **WHEN** `LoginAsync` is called AND `Network.IsConnected == true`, **THEN** response contains a `token` AND SecurePrefs stores credentials AND `AuthState` transitions to `LoggedIn`.
4. **GIVEN** SecurePrefs has a valid JWT AND `GET /auth/me` returns 200, **WHEN** `TryAutoLoginAsync` runs, **THEN** `AuthState` reaches `LoggedIn` AND no login screen shown AND `LoadPersistentAsync()` completed before `auth/init` was written.
5. **GIVEN** `BackendSettings.BackendMode == Offline`, **WHEN** game boots, **THEN** no auth calls are made AND player reaches game directly AND `AuthState` is derivable as `LoggedIn`.

## Test Evidence Path

- `Assets/_TinyRift/Tests/EditMode/AccountProfile/LoginServiceTests.cs`
- All 5 acceptance criteria as individual test methods
- Mock `IBackendService`, mock `INetworkManager`, mock `Save/Profile`
- Verify SecurePrefs interaction with mocked file system

## Dependencies

- **Save Story 001** — Core Persistence Layer (profile hydration via IPersistStateService)
- **Network Manager** — connection readiness gate

## Unlocks

- Hero Camp systems, Currency systems

## Risks

- **MEDIUM**: Template's `WebsocketAuthHandler` may have breaking changes on template update. Mitigation: thin facade insulates game code; only the facade needs updates.
