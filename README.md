<<<<<<< HEAD
# Aura — Student Attendance System

Aura is a school-grade student attendance management system with face recognition, QR/RFID scanning, geolocation check-in, governance hierarchy, sanctions, AI assistant, and reporting.

## Services

| Folder | Description |
|---|---|
| `backend/` | FastAPI API, Alembic migrations, Celery workers |
| `frontend-web/` | Vue 3 (Vite) SPA + Capacitor mobile |
| `frontend-apk/` | Capacitor Android native project |
| `assistant/` | Streaming LLM assistant with MCP tool integration |
| `database/` | Postgres service, schema docs, Docker init scripts |
| `seeder/` | Demo data seeder (dev only) |

## Quick Start

### Development

```powershell
# 1. Copy and configure each service's environment
Copy-Item backend\.env.example backend\.env
Copy-Item assistant\.env.example assistant\.env
Copy-Item database\.env.example database\.env
Copy-Item frontend-web\.env.example frontend-web\.env

# 2. Fill in the required values in each .env file

# 3. Start everything in dev mode (includes pgAdmin)
docker compose up --build postgres redis migrate bootstrap backend worker beat assistant frontend pgadmin log-viewer
```

When ready:

- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8001/docs`
- Assistant docs: `http://localhost:8500/docs`
- pgAdmin: `http://localhost:5050`
- Log viewer: `http://localhost:8080`

### Production

```powershell
docker compose --profile prod up --build
```

Production excludes pgAdmin. Make sure to set production values in each `.env` before deploying — see `SECURITY.md`.

## Database Seeding (Dev Only)

To populate the database with demo data:

```powershell
# In seeder/.env, set:
# SEED_DATABASE=true
# SEED_CONFIRM=yes
# SEED_WIPE_EXISTING=true

cd seeder
python seed.py demo
```

Or via Docker — the seeder service runs automatically if `SEED_DATABASE=true` and `SEED_CONFIRM=yes` are set in your `.env`.

## Environment Variables

Each service has its own `.env.example`. Copy it to `.env` and fill in the values.

Variables are tagged with one of four types:

- `[BEHAVIOR]` — controls how this service behaves. Independent — nothing else depends on this value.
- `[IDENTITY]` — credentials or secrets that define who this service is. Independent — you choose them, but other services may need to copy them into their own `[NEIGHBOR]` variables.
- `[ENDPOINT]` — this service's own address or port that other services connect to. You choose the value, but other services must match it.
- `[NEIGHBOR]` — URL or address of another service this service talks to. Dependent — must match the target service's `[ENDPOINT]` or `[IDENTITY]`.

## Documentation

- [Security Guide](SECURITY.md)
- [Backend docs](backend/docs/)
- [Frontend docs](frontend-web/docs/)
- [Assistant docs](assistant/docs/)
- [Database docs](database/)
- [Seeder docs](seeder/docs/)
- [Audit Report](frontend-web/docs/audits/AUDIT_REPORT.md)

## README Index

- [Assistant README](assistant/README.md)
- [Backend README](backend/README.md)
- [Database README](database/README.md)
- [Frontend README](frontend-web/README.md)
- [Frontend APK README](frontend-apk/README.md)
- [Seeder README](seeder/README.md)

## Notes

- Redis/Celery is required for background jobs (bulk import, email delivery).
- Non-secret backend defaults live in `backend/app/core/app_settings.py`.
- Non-secret assistant defaults live in `assistant/lib/app_settings.py`.
- Migrations run automatically on `docker compose up` via the `migrate` service.
=======
# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).

## Docker

This repo ships with a production-style Docker setup so the frontend can be demoed consistently without relying on a local Node install.

### Files

- `Dockerfile`
  Builds the Vue app with Vite, then serves the built files from Nginx.
- `docker-compose.yml`
  Starts the demo container and maps the app to a local port.
- `nginx.conf.template`
  Handles SPA routing and proxies backend requests from `/__backend__` to the configured backend origin.
- `runtime-config.js.template`
  Generates the runtime backend configuration file so the same build can point to a different cloud backend later.
- `public/runtime-config.js`
  Safe browser fallback for local development when no runtime override is injected.
- `.env.docker.example`
  Example runtime configuration for Docker.

### Container

- `aura-web`
  Serves the built Aura frontend on port `80`, keeps Vue Router working with `try_files`, forwards API requests to the external backend through `/__backend__`, and injects runtime backend config on container start.

### Start

1. Copy `.env.docker.example` to `.env.docker`.
2. Set `BACKEND_ORIGIN` to the backend root URL.
   Use the host root, not the `/api` suffix.
   Example: `https://your-ngrok-host.ngrok-free.dev`
3. Optional:
   - keep `AURA_API_BASE_URL=/__backend__` to use the built-in nginx proxy
   - or set `AURA_API_BASE_URL=https://your-cloud-api.example.com` to call the cloud API directly from the browser
   - if you use a direct cloud URL, make sure the backend allows your frontend origin with CORS
4. Run:

```bash
docker compose --env-file .env.docker up --build -d
```

5. Open:

```text
http://localhost:8080
```

### Stop

```bash
docker compose --env-file .env.docker down
```

### Health Check

The container exposes a simple health endpoint at `/healthz` for Docker health checks.

## Cloud Backend Flexibility

The frontend now resolves the backend in this order:

1. `window.__AURA_RUNTIME_CONFIG__.apiBaseUrl`
2. `VITE_API_BASE_URL`
3. default proxy path `/__backend__`

This means you can keep one frontend build and change only runtime config when the backend moves.

### Local Vite development

Use a proxy target in `.env.development.local`:

```env
VITE_API_BASE_URL=/__backend__
VITE_BACKEND_PROXY_TARGET=https://your-cloud-backend.example.com
```

### Docker demo

Use the nginx proxy:

```env
BACKEND_ORIGIN=https://your-cloud-backend.example.com
AURA_API_BASE_URL=/__backend__
```

### Static / cloud frontend hosting

Publish a `runtime-config.js` alongside the built app with:

```js
window.__AURA_RUNTIME_CONFIG__ = {
  apiBaseUrl: 'https://your-cloud-backend.example.com',
  apiTimeoutMs: 15000,
}
```

If your backend root is accidentally configured as `https://host/api`, Aura now normalizes that to the host root automatically to avoid duplicated `/api/api/...` requests.
>>>>>>> mr.frontend_v7
