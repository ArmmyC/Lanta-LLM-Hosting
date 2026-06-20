# Lanta Status Dashboard

Small admin service for platform health and operational links. Grafana remains
the source of truth for metrics and usage.

## Run

```powershell
docker compose -f dashboard/docker-compose.yml up -d --build
```

## Interfaces

- `GET /` redirects to `/status`.
- `GET /status` renders platform health.
- `GET /usage` links to Grafana.
- `GET /api/healthz` reports dashboard health.
- `GET /api/platform/status` returns component health.
- `GET /api/platform/usage` returns an experimental diagnostic summary.
