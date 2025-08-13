# AGENTS Backlog — Sprints 3–12 (Codex-Ready)

> **Scope**: This file continues after your existing Sprints 1–2. It details the next stages according to `requirements.md`, designed for execution by **OpenAI Codex** (agentic coding).  
> **Stack assumptions from requirements**: FastAPI services (Auth, Profile, Analytics), **Go** for Content service + **Python Celery** worker for media, **Node.js WS** for Chat, Envoy/NGINX gateway, GHCR images, Helm/K8s, PostgreSQL, MinIO, RabbitMQ, Redis.

---

## Conventions (for Codex and humans)

- **Task IDs**: `<PREFIX><sprint>.<index>` (e.g., `A3.2`, `PR4.3`, `C5.1`). Use them to prefix commit messages and PR titles.
- **Commit style**: Atomic changes only. Conventional prefixes: `feat:`, `fix:`, `chore:`, `docs:`. Example: `A3.2 feat: add refresh_tokens table + migration`.
- **File boundaries**: Each task lists *Files Codex Can Touch*. Do not modify anything outside of these lists unless explicitly allowed.
- **Tests & quality gates**:
  - Unit tests for all core paths and error cases.
  - Contract lint (`npx @stoplight/spectral-cli lint libs/contracts/*.yaml -D`).
  - Formatters/linters: Python (ruff/black), Go (gofmt/golangci-lint), Node (eslint/prettier).
  - Docker image build for the changed service. (including `Dockerfile` builds successfully on a clean machine)
  - Helm template & kube-linter validation.
  - Container runs as non-root, serves the FastAPI app on `${PORT:-8000}`, and `/healthz` returns 200.
  - `.dockerignore` prevents large/unnecessary context.
  - Helm `values.yaml` contains image repo/tag and probes for Auth.
  - GitHub Actions workflow builds the image and pushes to GHCR on `main` pushes; PRs build without pushing.
  - No secrets are added to the image or committed to Git.
- **Security rules**: Never commit secrets. JWT validation (aud/iss), CSRF for cookies if used, rate limits, lockouts per requirements.
- **Migrations**: Always idempotent; include `upgrade`/`downgrade`. Avoid destructive changes unless a dedicated migration task says so.
- **Observability**: `/healthz`, `/readyz`, `/metrics` for every service; structured logs (JSON); correlation IDs from gateway.
- **Gateway**: Routes defined per service; JWT enforced at edge for protected routes; `x-request-id` propagation.
- **Artifacts**: Every task finishes with a list of changed files for PR description.

---

## Codex Run Template (paste into each task prompt)

**Instruction to Codex**:  
- You may only modify the files listed under *Files to touch*.  
- Keep changes minimal and scoped to the task.  
- Produce unit tests for new code paths.  
- When done, output a summary with file paths changed and commands to run tests locally.

**Local checks** (run in CI and locally):
```
# Contracts
npx @stoplight/spectral-cli lint libs/contracts/*.yaml -D

# Service-specific
# Python
ruff . && black --check . && pytest -q
# Go
gofmt -l . && golangci-lint run && go test ./...
# Node
eslint . && npm test -s

# Docker build (service)
docker build -f services/<service>/Dockerfile services/<service>

# Helm sanity
helm template deploy/helm/<service> | kubeval --ignore-missing-schemas
```
---

# Sprint 3 — Auth edges & hardening
**Prefix**: `A3.*`  
**Goal**: Finish flows from `requirements.md` §Auth: email flows, rotation, lockouts, rate limits, refresh model, probes/metrics.

### A3.1 — Contracts: complete `auth.yaml`
**Files to touch**
- `libs/contracts/auth.yaml`
- `libs/contracts/.spectral.yaml`

**Steps**
1. Add paths/schemas for: register/verify (email), login (email+password), password reset (request/confirm), logout, refresh, email/phone update.  
2. Error models: 400/401/423/429 with stable structure.  
3. Lint with Spectral.

**DoD**
- All endpoints described; Spectral passes in CI.

---

### A3.2 — DB migrations & models
**Files to touch**
- `services/auth/app/db/migrations/*`
- `services/auth/app/db/models.py`
- `services/auth/app/schemas.py`

**Steps**
1. Create tables: `users`, `email_verifications`, `password_resets`, `refresh_tokens`.  
2. Add required indices (unique email, token lookup, user+family for refresh).  
3. Alembic migration with upgrade/downgrade.

**DoD**
- `alembic upgrade head` green; tables present; tests cover model constraints.

---

### A3.3 — Email flows (register/verify/login/reset)
**Files to touch**
- `services/auth/app/routers/email.py`
- `services/auth/app/services/email_flows.py`
- `services/auth/app/security/tokens.py`
- `services/auth/app/main.py` (router include)
- `services/auth/tests/test_email_flows.py`

**Steps**
1. **Register**: create inactive user + verification token (TTL 24h).  
2. **Verify**: activate user, mint access(1h)+refresh(30–60d), invalidate verification token.  
3. **Login**: validate password, rotate refresh, optional device metadata.  
4. **Reset password**: request token (TTL 15m), confirm flow invalidates all refresh tokens.  
5. Return structured errors; emit events (`user.registered`, `auth.password_reset`).

**DoD**
- Unit tests for happy/error paths; contract tests pass.

---

### A3.4 — Phone lockouts, rate limits, token family rotation
**Files to touch**
- `services/auth/app/services/phone_flows.py`
- `services/auth/app/security/rate_limit.py`
- `services/auth/app/security/refresh_family.py`
- `services/auth/tests/test_limits_rotation.py`

**Steps**
1. Rate limits: 30s/phone send, 5/hr per IP.  
2. OTP attempts: max 5/code, then lock 1h.  
3. Refresh token families with `prev_id`, `revoked_at`; revoke family on password reset; rotate on use.

**DoD**
- E2E tests show correct 429/423; JWTs contain expected claims; rotation works.

---

### A3.5 — Helm, probes, metrics, HPA
**Files to touch**
- `deploy/helm/auth/templates/deployment.yaml`
- `deploy/helm/auth/values.*.yaml`
- `services/auth/app/metrics.py`
- `services/auth/app/main.py` (expose `/healthz`, `/readyz`, `/metrics`)

**Steps**
1. Add health/readiness probes; Prom metrics.  
2. HPA: CPU>70%; requests/limits defined.  
3. Sample Grafana dashboard JSON (optional).

**DoD**
- Helm deploy to `dev` succeeds; HPA scales under k6 load; metrics visible.

---

### A3.6 — Containerize Auth (Dockerfile, .dockerignore, CI, Helm)
**Goal**: Build a production-grade container for the Auth FastAPI service completed in A3.1–A3.5. Use a multi-stage image, run as non-root, expose health endpoints, and hook into CI + Helm.

**Files to touch**
- `services/auth/Dockerfile`
- `services/auth/.dockerignore`
- `deploy/helm/auth/values.yaml`
- `.github/workflows/docker-auth.yml` (new, minimal build & push to GHCR)

**Assumptions**
- App entrypoint: `services/auth/app/main.py` exposes app (FastAPI).
- Python version: 3.12 (adjust if `pyproject.toml/requirements.txt` says otherwise).
- Health endpoints from A3.5: `/healthz`, `/readyz`, `/metrics`.

**DoD**
- `services/auth/Dockerfile` builds successfully on a clean machine.
- Container runs as non-root, serves the FastAPI app on `${PORT:-8000}`, and `/healthz` returns 200.
- `.dockerignore` prevents large/unnecessary context.
- Helm `values.yaml` contains image repo/tag and probes for Auth.
- GitHub Actions workflow builds the image and pushes to GHCR on `main` pushes; PRs build without pushing.
- No secrets are added to the image or committed to Git.

---

# Sprint 4 — Profile Service (FastAPI)
**Prefix**: `PR4.*`  
**Goal**: User profiles with history, avatar storage via MinIO, admin CRUD for experience levels.

### PR4.1 — Contracts & DB
**Files to touch**
- `libs/contracts/profile.yaml`
- `services/profile/app/db/migrations/*`
- `services/profile/app/db/models.py`
- `services/profile/app/schemas.py`

**Steps**
1. Define `GET/PUT /api/profile` + models.  
2. Add `profiles`, `experience_levels`, `social_bindings`, `profile_history`.  
3. Spectral lint.

**DoD**
- Migrations green; contracts lint clean.

---

### PR4.2 — Profile CRUD + diff history
**Files to touch**
- `services/profile/app/routers/profile.py`
- `services/profile/app/services/profile_service.py`
- `services/profile/tests/test_profile.py`

**Steps**
1. `GET/PUT` using JWT `sub` as user id.  
2. On PUT, compute diffs and append to `profile_history` (field, old, new, ts, actor).  
3. Validate enums/lengths per requirements.

**DoD**
- Tests cover diff logging and validations.

---

### PR4.3 — Avatar upload via MinIO (presigned URLs)
**Files to touch**
- `services/profile/app/routers/avatar.py`
- `services/profile/app/storage/minio_client.py`
- `libs/contracts/profile.yaml` (add `/api/profile/avatar/presign`)
- `deploy/helm/profile/values.*.yaml`

**Steps**
1. `POST /avatar/presign` → presigned PUT (<=5MB; jpeg/png).  
2. After upload, finalize and persist `avatar_url`.  
3. Optionally expose short-lived GET for secure display.

**DoD**
- Manual happy path works; content-type and size enforced.

---

### PR4.4 — Admin CRUD for experience levels
**Files to touch**
- `services/profile/app/routers/admin_experience.py`
- `services/profile/tests/test_admin_experience.py`

**Steps**
1. `GET/POST/PUT/DELETE /api/admin/experience-levels`.  
2. Require `admin` role claim at gateway + in-service check.

**DoD**
- 403 for non-admin; full CRUD happy path tested.

---

# Sprint 5 — Content Service (Go API)
**Prefix**: `C5.*`  
**Goal**: Replace FastAPI stub with Go HTTP API; CRUD for courses/sections/materials; upload lifecycle.

### C5.1 — Contracts and service switch
**Files to touch**
- `libs/contracts/content.yaml`
- `services/content/go.mod`
- `services/content/cmd/server/main.go`
- `services/content/internal/{http,db,storage}`
- `services/content/Dockerfile`
- `deploy/helm/content/*`

**Steps**
1. Expand contract (`courses`, `sections`, `materials`, `media_assets`, `tags`).  
2. Scaffold server (chi/echo/gin): `/healthz`, `/api/content/*`.  
3. Replace CI matrix to build Go image.

**DoD**
- Content image builds/pushes; gateway routes updated; contract tests pass.

---

### C5.2 — DB schema & migrations (Go)
**Files to touch**
- `services/content/internal/db/migrations/*.sql`
- `services/content/internal/db/models.go`
- `services/content/internal/db/repo_test.go`

**Steps**
1. Create tables: `courses`, `sections`, `materials`, `media_assets`, `tags`, `course_tags`.  
2. Indices and FKs; CASCADE where safe.  
3. Repository tests for basic ops.

**DoD**
- Migrations apply; tests green.

---

### C5.3 — Presigned uploads & asset lifecycle
**Files to touch**
- `services/content/internal/storage/minio.go`
- `services/content/internal/http/handlers_upload.go`
- `services/content/internal/http/handlers_assets.go`

**Steps**
1. `POST /materials/{id}/upload/presign` → PUT URL with size/type constraints.  
2. Finalize: move to `media_assets`, `status=ready`, enqueue transcode task for worker.

**DoD**
- 50MB upload works; wrong MIME rejected; event enqueued.

---

### C5.4 — Course & material CRUD + publish workflow
**Files to touch**
- `services/content/internal/http/handlers_courses.go`
- `services/content/internal/http/handlers_materials.go`
- `services/content/internal/domain/workflow.go`
- `services/content/internal/http/tests/*`

**Steps**
1. Status machine: `draft → review → published`.  
2. Filters: status, tags, author, search.  
3. Validate transitions + RBAC where needed.

**DoD**
- Contract tests green; 400 on invalid transitions.

---

# Sprint 6 — Content Worker (Python Celery)
**Prefix**: `CW6.*`  
**Goal**: Media transcoding with ffmpeg HLS presets and retries; update asset status.

### CW6.1 — Worker skeleton & queueing
**Files to touch**
- `services/content-worker/app/worker.py`
- `services/content-worker/app/tasks/transcode.py`
- `deploy/helm/content-worker/*`
- `services/content-worker/requirements.txt`
- `services/content-worker/Dockerfile`

**Steps**
1. Celery app bound to RabbitMQ; durable queues.  
2. Accept `asset_id`, `source_path`, `preset`.  
3. Logging + Prom metrics for retries.

**DoD**
- Task published by Content service is consumed and logged.

---

### CW6.2 — ffmpeg presets & lifecycle updates
**Files to touch**
- `services/content-worker/app/tasks/transcode.py`
- `services/content-worker/app/presets.yaml`
- `services/content-worker/app/clients/content_api.py`
- `services/content-worker/tests/test_transcode.py`

**Steps**
1. Implement HLS 720p/1080p; 3 retries w/ exponential backoff.  
2. On success, update asset in Content API (`status=ready`, renditions).  
3. On final failure, set `status=failed` + reason.

**DoD**
- Sample MP4 → HLS stored in MinIO; status transitions correct; tests cover retry logic.

---

# Sprint 7 — Notifications Service
**Prefix**: `N7.*`  
**Goal**: Templates, providers, queueing, and system event wiring.

### N7.1 — Contracts & templates
**Files to touch**
- `libs/contracts/notifications.yaml`
- `services/notifications/app/templates/email/*.mjml`
- `services/notifications/app/templates/sms/*.txt`
- `services/notifications/app/templates/push/*.json`

**Steps**
1. Define `/api/notify/send`, `/api/notify/preview`, `/api/subscriptions/*`.  
2. Template variables stable and documented.

**DoD**
- Spectral lint OK; preview renders for each channel.

---

### N7.2 — Providers & retry/DLQ
**Files to touch**
- `services/notifications/app/providers/{email.py,sms.py,push.py}`
- `services/notifications/app/routers/notify.py`
- `services/notifications/app/worker.py`
- `services/notifications/tests/test_providers.py`

**Steps**
1. Implement provider interfaces; idempotency keys; retries on 5xx, DLQ on hard errors.  
2. Queue send requests; expose `/preview` for testing.

**DoD**
- Simulated providers pass; retry/DLQ behavior covered in tests.

---

### N7.3 — System events wiring
**Files to touch**
- `services/*/app/events.py` (emitters in Auth/Content)
- `services/notifications/app/subscribers.py`
- `services/notifications/tests/test_subscribers.py`

**Steps**
1. Emit: `user.registered`, `auth.password_reset`, `content.published`.  
2. Subscribe and fan-out notifications per user subscriptions.

**DoD**
- Registering a user triggers welcome email end-to-end.

---

# Sprint 8 — Chat Service (Node.js + Redis) — Part 1
**Prefix**: `CH8.*`  
**Goal**: WS server, contracts, gateway integration, presence with Redis.

### CH8.1 — Service switch & contracts
**Files to touch**
- `libs/contracts/chat.yaml`
- `services/chat/src/index.ts`
- `services/chat/package.json`
- `services/chat/tsconfig.json`
- `services/chat/Dockerfile`
- `deploy/helm/chat/*`

**Steps**
1. Describe WS handshake route, REST for history/search, presence.  
2. Implement WS server (ws/uWebSockets.js); JWT auth on connection; room model (dm/group).  
3. Build Node image in CI; gateway route.

**DoD**
- Basic handshake OK via gateway; contract lint passes.

---

### CH8.2 — Redis & presence
**Files to touch**
- `services/chat/src/redis.ts`
- `services/chat/src/presence.ts`
- `services/chat/tests/presence.test.ts`

**Steps**
1. Track `online:{userId}` with TTL; pub/sub for presence changes.  
2. Broadcast presence to room members; ensure <1s propagation across pods.

**DoD**
- Presence tests pass; manual multi-pod test OK.

---

# Sprint 9 — Chat Service — Part 2
**Prefix**: `CH9.*`  
**Goal**: Message history in PostgreSQL, pagination, moderation, rate limits, attachments (MinIO).

### CH9.1 — Message store & pagination
**Files to touch**
- `services/chat/src/db/*` (ORM of choice)
- DB migrations for `dialogs`, `messages`, `attachments`
- `services/chat/src/http/history.ts`
- `services/chat/tests/history.test.ts`

**Steps**
1. Append-only messages; cursor pagination; soft delete.  
2. Attachment presign reusing MinIO pattern.

**DoD**
- 1M msgs load: pagination <200ms P95; tests green.

---

### CH9.2 — Moderation & rate limits
**Files to touch**
- `services/chat/src/moderation.ts`
- `services/chat/src/rate_limit.ts`
- `services/chat/tests/rate_moderation.test.ts`

**Steps**
1. Per-user limit (e.g., 20 msg / 10s).  
2. Blocklist + simple profanity filter (pluggable).  
3. Admin delete audited.

**DoD**
- Flood tests return 429; moderation hooks covered by tests.

---

# Sprint 10 — Analytics Service
**Prefix**: `AN10.*`  
**Goal**: Ingest events, basic reports, scheduled PDFs to MinIO.

### AN10.1 — Contracts & ingestion
**Files to touch**
- `libs/contracts/analytics.yaml`
- `services/analytics/app/routers/ingest.py`
- `services/analytics/app/db/migrations/*`
- `services/analytics/app/db/models.py`
- `services/analytics/tests/test_ingest.py`

**Steps**
1. `/api/analytics/ingest` (batch).  
2. Table `events` (jsonb payload, ts, user_id, type, src).  
3. Backpressure on oversize batches (413).

**DoD**
- 5k events/s sustained in dev; tests for schema and limits.

---

### AN10.2 — Query endpoints & exports
**Files to touch**
- `services/analytics/app/routers/reports.py`
- `services/analytics/tests/test_reports.py`

**Steps**
1. DAU/WAU/retention; course completion; funnel per requirements.  
2. CSV/XLSX streaming exports.

**DoD**
- Under 2s on 10M rows with indexes/materialized views.

---

### AN10.3 — PDF dashboards (worker)
**Files to touch**
- `services/analytics/app/worker.py`
- `deploy/helm/analytics/*`
- `services/analytics/app/clients/storage.py`

**Steps**
1. Celery job to render PDF on schedule/on-demand.  
2. Store into MinIO; presigned GET returned to caller.

**DoD**
- Scheduled report appears in MinIO and can be downloaded.

---

# Sprint 11 — Security Hardening
**Prefix**: `SEC11.*`  
**Goal**: Harden headers, JWT strictness, secrets handling, RBAC, SAST/dependency scanning.

- **SEC11.1 — Edge headers**: Add CSP, HSTS, Referrer-Policy at gateway; tests verify.  
- **SEC11.2 — JWT validation**: Enforce `aud/iss`, clock skew; short access TTL; refresh rotation everywhere.  
- **SEC11.3 — Secrets**: GitHub Environments/Actions; no secrets in URLs; rotate provider keys.  
- **SEC11.4 — RBAC review**: Admin endpoints gated at gateway and in service.  
- **SEC11.5 — SAST/Deps scan**: CodeQL + `npm audit`/`pip-audit`/`govulncheck` in CI.

**DoD**
- ZAP baseline clean; header checks pass; scans green or triaged.

---

# Sprint 12 — Observability & Performance
**Prefix**: `OBS12.*`  
**Goal**: Unified metrics, tracing, structured logs, HPA tuning, load tests, SLOs/alerts.

- **OBS12.1 — Metrics**: Prometheus `/metrics` across services; Grafana dashboards.  
- **OBS12.2 — Tracing**: OpenTelemetry propagation via gateway; spans visible in collector.  
- **OBS12.3 — Logs**: JSON logs; correlation IDs from gateway; sample logs as CI artifact.  
- **OBS12.4 — HPA tuning**: Load tests for auth/content/chat; resource requests calibrated.  
- **OBS12.5 — SLOs & alerts**: Latency P95, error budget, queue depth, worker retries.

**DoD**
- k6/Gatling scripts pass targets; alert rules firing appropriately in dev.

---

## Dependencies & Sequencing

- **A3** → **PR4** → **C5/CW6** → **N7** → **CH8/CH9** → **AN10** → **SEC11** → **OBS12**  
- Contracts and migrations must precede service implementation.  
- Gateway routes updated as services come online.

---

## Global Definition of Done (for each PR)

1. All listed unit tests added and passing; coverage doesn’t drop.  
2. Contract lint green; if contract changed, version bumped with changelog.  
3. Docker image builds and runs locally.  
4. Helm template validates; environment values documented.  
5. No secrets committed; GOPATH/NPM/Python lock files updated.  
6. PR description lists changed files and manual validation steps.  
