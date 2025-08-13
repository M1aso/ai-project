# BACKLOG_codex_github.md

> **Purpose**: A step-by-step, **Codex-friendly** backlog to build and ship the backend of the corporate e‑learning platform via **GitHub** (Actions, Environments, GHCR).  
> **Rule of engagement** for codegen: *touch only the files listed per task; keep all scripts idempotent; use small, readable commits prefixed with the task ID.*

## Global standards (read once)
- **Architecture**: microservices behind an Envoy API Gateway; NGINX Ingress at the edge; JWT validated at the gateway; service-level **authorization**.
- **Languages**: Auth/Profile/Notifications/Analytics = **Python (FastAPI)**; Content = **Go (HTTP)**; Chat = **Node.js (WS)**; workers = **Python Celery**.
- **Data plane**: PostgreSQL (HA), MinIO (object storage, **presigned URLs**), RabbitMQ (tasks), Redis (chat backplane).
- **CI/CD**: GitHub Actions — build → push to **GHCR** → Helm deploy to `dev | staging | prod` (GitHub Environments).
- **Security**: short‑lived access tokens, rotating refresh tokens; strict JWT validation; HSTS/CSP at edge; no secrets in URLs.
- **Definition of Done (per task)**: Lint/tests green in CI; images in GHCR; Helm upgrade to env OK; probes & metrics pass.

## Repo layout
```
/services/{auth,profile,content,notifications,chat,analytics}
/libs/contracts
/deploy/helm/{api-gateway,auth,profile,content,notifications,chat,analytics}
/tests/perf
/.github/workflows
/.github/ISSUE_TEMPLATE
```
---

# Sprint 0 — GitHub plumbing

### G0.1 — Initialize repo skeleton
**Files**
- create folders as per layout; add `README.md` in root + each service (one-liner).

**Steps**
1) Create directories.
2) Add minimal readmes.

**DoD**
- Tree matches layout; no stray files.

---
### G0.2 — Contracts workspace (OpenAPI 3.1) + Spectral lint
**Files**
- `libs/contracts/.spectral.yaml`
- `libs/contracts/{auth,profile,content,notifications,chat,analytics}.yaml` (stubs included in this kit)

**Steps**
1) Add Spectral config.
2) Author minimal 3.1 stubs with `/healthz` for each service.

**DoD**
- `npx @stoplight/spectral-cli lint libs/contracts/*.yaml` exits 0 (wired into CI).

---
### G0.3 — GitHub Actions: **CI** (lint → test → build → push to GHCR)
**Files**
- `.github/workflows/ci.yml`

**Steps**
1) Lint OpenAPI with Spectral.
2) Run unit tests (placeholders OK for now).
3) Build Docker for each service; push to `ghcr.io/<org>/<service>:<sha>`.

**DoD**
- CI is green; images visible in GHCR.

---
### G0.4 — GitHub Actions: **Deploy** with Helm
**Files**
- `.github/workflows/deploy.yml`

**Steps**
1) Manual dispatch: input `environment = dev|staging|prod`.
2) Auth to cluster (kubeconfig secret or OIDC).
3) `helm upgrade --install` for api-gateway + services.

**DoD**
- Manual run to `dev` completes; resources healthy.

---
### G0.5 — GitHub Environments & Secrets
**Action**
- Create envs `dev|staging|prod`; add secrets: `KUBE_CONFIG` (or OIDC), `REGISTRY=ghcr.io`, `REGISTRY_USER`, `REGISTRY_TOKEN`.  
- Add DB and app secrets as service vars later.

**DoD**
- Workflows can `kubectl get ns` and pull/push images.

---

# Sprint 1 — Platform: ingress, gateway, limits, deps

### P1.1 — Namespaces & RBAC (bootstrap)
**Files**
- `deploy/k8s/namespaces.yaml` (create in your repo; apply in deploy workflow pre-step)

**DoD**
- Namespaces `dev|staging|prod` exist.

---
### P1.2 — Ingress (NGINX) with WebSockets
**Files**
- `deploy/helm/*/templates/ingress.yaml`

**Steps**
1) Add standard Upgrade/Connection headers.
2) One host or path per service under `/api/<svc>/*` (example in chart).

**DoD**
- `/healthz` reachable; WS handshake for chat works.

---
### P1.3 — Envoy API Gateway with **jwt_authn**
**Files**
- `deploy/helm/api-gateway/templates/configmap.yaml` (Envoy)
- `deploy/helm/api-gateway/values.*.yaml`

**Steps**
1) Configure `jwt_authn` with your `issuer` and JWKS.
2) Route `/api/*` → upstream services; forward verified claims in headers.

**DoD**
- Missing/invalid JWT → 401 at gateway; valid JWT → reaches service with claims.

---
### P1.4 — Edge rate limiting for `/api/auth/*`
**Files**
- ingress annotations/policies in each service’s `ingress.yaml`

**Steps**
1) Per‑IP RPS limit.
2) Optional: per‑phone key (hash header via annotation/sidecar).

**DoD**
- Synthetic burst test returns 429 as configured.

---
### P1.5 — Core dependencies online
**Action**
- Provision PostgreSQL, MinIO bucket(s), RabbitMQ, Redis; add connection secrets to envs.

**DoD**
- From a toolbox pod: PG auth OK; MinIO presigned PUT/GET OK; RabbitMQ publish/consume OK; Redis PING OK.

---

# Sprint 2–3 — Auth Service (FastAPI)
**Task IDs: A2.***

- **A2.1 DB migrations** — `users`, `sms_codes`, `refresh_tokens` (SQL from spec).  
- **A2.2 Contract** — endpoints exactly as spec.  
- **A2.3 Service skeleton** — healthz/readyz, JWT mint/verify helpers.  
- **A2.4 Phone send‑code** — validate `+7` E.164; 30s/phone & 5/hr/IP; save `sms_codes`; call provider.  
- **A2.5 Phone verify** — TTL 5m; attempts<5; lock 1h; create user if new; issue `access_token(1h)` + `refresh_token(30|60d)`; invalidate SMS on success.  
- **A2.6 Email flows** — register (inactive+email_token TTL 24h), confirm (activate & invalidate RTs), login, forgot/reset (reset TTL 15m + invalidate RTs).  
- **A2.7 Logout** — delete refresh token.  
- **A2.8 Helm/metrics/probes** — HPA works, Prometheus metrics exposed.

**DoD**
- Contract tests pass; 401/423/429 covered; gateway rejects bad JWTs.

---

# Sprint 4 — Profile Service
**Task IDs: PR4.***

- **PR4.1 DB** — `profiles`, `experience_levels`, `social_bindings`, `profile_history`.
- **PR4.2 GET/PUT /api/profile** — record `profile_history` per field.
- **PR4.3 Avatar upload** — presigned PUT (<=5MB; jpeg/png); store `avatar_url`.
- **PR4.4 Experience levels** — admin CRUD.

**DoD**
- Audit trail visible; avatar flow browser→MinIO direct.

---

# Sprint 5–6 — Content Service (Go API + Python worker)
**Task IDs: C5.***

- **C5.1 DB** — `courses`, `sections`, `materials`, `media_files`, `transcode_jobs`, `documents`.
- **C5.2 CRUD** — courses/sections/materials; students see **published** only.
- **C5.3 Upload** — presigned PUT for video/docs; create `media_files`/`documents`; enqueue `transcode_jobs`.
- **C5.4 Worker** — Celery task runs **ffmpeg → HLS** (480p/720p/1080p), uploads results, sets `ready|failed` with `output_url`.
- **C5.5 Status/stream** — `/media/:id/status`; `/stream?bitrate=` → 302 to HLS manifest (optionally signed).

**DoD**
- End‑to‑end upload → HLS playable; failures logged and visible.

---

# Sprint 7 — Notifications Service
**Task IDs: N7.***

- **N7.1 DB** — notification types, settings, templates, queue.
- **N7.2 API** — settings & template CRUD (Mustache body).
- **N7.3 Workers** — enqueue & deliver SMTP + Telegram; retries with backoff; DLQ on hard fail.

**DoD**
- Status `pending→sent|failed`, attempts & last_error populated.

---

# Sprint 8–9 — Chat Service (Node WS + Redis)
**Task IDs: CH8.***

- **CH8.1 DB** — chats, participants, messages, attachments.
- **CH8.2 REST** — list chats, history, post/edit/delete, moderator delete.
- **CH8.3 WebSocket** — `ws://.../ws/chats/:id`; publish events via **Redis Pub/Sub**; broadcast to all nodes.

**DoD**
- 1k concurrent WS in `dev` echo messages with <1s fan-out.

---

# Sprint 10 — Analytics Service
**Task IDs: AN10.***

- **AN10.1 DB** — report types/requests/results/schedules.
- **AN10.2 API** — dashboard & report lifecycle (queue → ready); store PDF/XLSX in MinIO (WeasyPrint + Pandas).
- **AN10.3 Schedules** — Celery beat or cron to enqueue.

**DoD**
- Large dataset export stable; downloads work when `ready`.

---

# Sprint 11 — Security hardening
- Resource‑level authorization everywhere (roles/ownership).
- HSTS/CSP at edge; secrets in K8s Secrets; RT rotation.
- OTP abuse protection: confirm ingress limits + provider limits; exponential backoff; temporary block list.

**DoD**
- Security checklist signed off; pen‑test findings triaged.

---

# Sprint 12 — Observability & performance
- Prometheus metrics in every service; Grafana dashboards (HTTP rates, latency, errors, queue lag, WS connections).
- k6 tests in `tests/perf/` with thresholds (error rate <1%, p95 latency per endpoint). CI must fail on breach.

**DoD**
- Dashboards live; CI gate protects regressions.

---

## Commit message convention
```
<ID> <scope>: <change>
Body: why/what
Refs: link or issue #
```
Examples:
- `A2.4 auth: implement /api/auth/phone/send-code with server guardrails`
- `C5.4 content-worker: add ffmpeg HLS presets + retries`

---

## Appendix — Minimal runbooks
- **JWT at the gateway**: configure Envoy `jwt_authn` with `issuer`, `audiences`, and JWKS; forward verified claims to services.
- **Ingress WS**: ensure `Upgrade` / `Connection` headers are passed; NGINX Ingress supports WebSockets by default.
- **Presigned uploads**: APIs return presigned **PUT** for upload and presigned **GET** for limited-time reads; clients upload directly to MinIO.
- **Celery + RabbitMQ**: durable queues, publisher confirms, consumer acks; DLQ for hard failures.
- **Redis Pub/Sub**: best‑effort (at‑most‑once) fan‑out for chat; switch to Streams if persistence is required.
