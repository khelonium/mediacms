# Decisions

## 2026-03-01

- **Technique data lives in `files/data/techniques.json`** — single JSON tree consumed by the React frontend; Django view reads and serves it via template context.
- **Rebuilt bundles committed to `static/`** — production deploy uses pre-built JS/CSS; source of truth is `frontend/src/`, bundles are rebuilt with `node:14-bullseye` in Docker.

## 2026-02-28

- **`Dockerfile.local` uses Python 3.9 / Bullseye** — upstream uses EOL Python 3.8 / Buster; keeps us on supported base.
- **Local Docker build, not Docker Hub pull** — upstream image has Django 5.x incompatibilities.
- **allauth 0.44.0: no `AccountMiddleware`** — that middleware doesn't exist in this pinned version; do not add it.
- **Black line-length stays at 200** — matches upstream `pyproject.toml`; changing it would cause a massive reformatting diff.
- **Makefile over shell scripts** — preferred for Docker-primary projects; `make up`, `make down`, `make check`.
