# DevPulse

**A lightweight service observability platform for uptime checks, latency tracking, incident history and Prometheus metrics.**

DevPulse monitors HTTP services, stores check results, evaluates alert rules and exposes application metrics for Prometheus. It includes a REST API and a small dashboard-ready data model.

> **Status:** functional portfolio MVP. Checks are triggered through the API; a background scheduler, authentication and multi-tenant isolation are future work.

## Features

- Register and manage HTTP service targets
- Trigger HTTP health checks with configurable timeouts
- Persist status code, latency, availability and error details
- Evaluate latency and availability alert thresholds
- Maintain an incident/event history
- Expose Prometheus metrics at `/metrics`
- Structured health endpoint and OpenAPI docs
- Docker Compose, PostgreSQL and automated tests

## Architecture

```text
                 +-----------------------+
                 |      Dashboard        |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |     FastAPI API       |
                 +----+-------------+----+
                      |             |
               Target registry   Check runner
                                    |
                                    v
                              HTTP services
                                    |
                                    v
                 +-----------------------+
                 | Check results +       |
                 | alert evaluation      |
                 +-----------+-----------+
                             |
                   +---------+---------+
                   |                   |
                   v                   v
              PostgreSQL          Prometheus
                                  /metrics
```

## Stack

Python 3.12 · FastAPI · SQLAlchemy 2 · PostgreSQL · httpx · Prometheus Client · pytest · Docker

## Quick start

### Docker

```bash
git clone https://github.com/asunavlr/dev-pulse.git
cd dev-pulse
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Prometheus metrics: http://localhost:8000/metrics
- Health: http://localhost:8000/health

### Local development

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn devpulse.main:app --reload
pytest
```

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health |
| GET | `/metrics` | Prometheus exposition format |
| POST | `/targets` | Register a monitored HTTP target |
| GET | `/targets` | List targets |
| GET | `/targets/{id}` | Target details and latest check |
| DELETE | `/targets/{id}` | Delete target and its history |
| POST | `/targets/{id}/check` | Execute an HTTP check |
| GET | `/targets/{id}/checks` | Recent check history |
| GET | `/incidents` | List alert events |

### Register a target

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Example API","url":"https://httpbin.org/status/200","timeout_seconds":5,"latency_threshold_ms":800}'
```

### Run a check

```bash
curl -X POST http://localhost:8000/targets/1/check
```

A check records the HTTP status, duration and outcome. A failed request or a latency threshold breach creates an incident event. Repeated checks can resolve an active incident when the service recovers.

## Prometheus metrics

DevPulse exports:
- `devpulse_checks_total{target,status}`
- `devpulse_check_duration_seconds{target}`
- `devpulse_target_up{target}`

Example Prometheus scrape configuration:

```yaml
scrape_configs:
  - job_name: devpulse
    static_configs:
      - targets: ["devpulse:8000"]
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | SQLite file | SQLAlchemy URL |
| `DEFAULT_TIMEOUT_SECONDS` | `5` | Default outbound HTTP timeout |
| `MAX_TIMEOUT_SECONDS` | `30` | Maximum target timeout |
| `CHECK_HISTORY_LIMIT` | `100` | Maximum returned history rows |

## Security notes

- Target URLs are user-supplied. This MVP is intended for trusted, local/demo environments; do not expose target registration to untrusted users.
- Production deployment should enforce outbound network allowlists and block loopback, private, link-local and cloud metadata addresses to prevent SSRF.
- Authentication, RBAC, tenant isolation and audit controls are not implemented yet.
- Checks are manually triggered; no scheduler or distributed worker is included yet.

## Roadmap

- [ ] Background scheduler and distributed workers
- [ ] OpenTelemetry traces and context propagation
- [ ] Alert routing (email, Slack, webhooks)
- [ ] SLOs, error budgets and burn-rate alerts
- [ ] Multi-region probes
- [ ] Authentication, RBAC and tenant isolation
- [ ] Dashboard with live charts and incident timeline
- [ ] Network egress policy and SSRF protection

## License

MIT
