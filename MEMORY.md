# Decision Log

## 2026-02-28 — Local Docker Build Setup

**Context:** Upstream MediaCMS Docker Hub image (`mediacms/mediacms`) ships Django 5.x
which is incompatible with the codebase's `requirements.txt` (Django 3.x era). The
upstream `Dockerfile` uses Python 3.8 on Debian Buster, both of which are EOL.

**Decision:** Created `Dockerfile.local` using `python:3.9-bullseye` and modified
`docker-compose.yaml` to build locally (`build: context: . dockerfile: Dockerfile.local`)
instead of pulling from Docker Hub.

**Rationale:**
- Python 3.9 is the oldest still-supported CPython at time of writing.
- Bullseye is the matching Debian release for the 3.9 slim image.
- Building locally ensures the container matches the repo's pinned requirements.

---

## 2026-02-28 — allauth Middleware

**Context:** Django 4.2+ projects using allauth ≥ 0.56 need
`allauth.account.middleware.AccountMiddleware`. Our fork pins allauth 0.44.0.

**Decision:** Do **not** add `AccountMiddleware` to `MIDDLEWARE`.

**Rationale:** allauth 0.44.0 predates that middleware class; adding it would cause an
`ImportError` at startup.

---

## 2026-02-28 — Black Line Length

**Context:** `pyproject.toml` sets `line-length = 200`. Upstream uses this setting.

**Decision:** Keep `line-length = 200` (do not change to PEP 8's 79 or common 88/120).

**Rationale:** Changing it would produce a massive reformatting diff that makes future
upstream merges painful. Style consistency within the project matters more than convention.
