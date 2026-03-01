# Deploy Guide

Production: `bjj.chadao.ro` | User: `root` | Dir: `/mediacms/cms/mediacms`

## Architecture

Production uses `docker-compose-letsencrypt.yaml` with **volume mounts** (`./:/home/mediacms.io/mediacms/`). This means:
- Code changes take effect after `git pull` + container restart (no image rebuild needed)
- `prestart.sh` runs `migrate` + `collectstatic` on the `migrations` container start
- The web container serves whatever is in `static/` via uWSGI + Nginx

## Deploy Checklist

### Quick deploy (code-only changes)

```bash
make deploy
```

This runs: `deploy-pull` → `deploy-static` → `deploy-restart` → `deploy-verify`

### Step-by-step (when troubleshooting)

#### 1. Build frontend locally

The Dockerfile does **NOT** run `npm run dist`. Built JS/CSS must be committed.

```bash
make frontend-build       # builds + copies to static/
git add static/js/ static/css/
git commit -m "chore: rebuild frontend"
git push origin main
```

#### 2. Pull on server

```bash
make deploy-pull
# or: ssh root@bjj.chadao.ro "cd /mediacms/cms/mediacms && git pull origin main"
```

#### 3. Fix collectstatic source directory

`STATICFILES_DIRS` points to `frontend/dist/static/` which doesn't exist on the server (created by `npm run dist` locally). Must populate it for `collectstatic` to work:

```bash
make deploy-static
```

This creates `frontend/dist/static/` and copies all static assets there, then runs `collectstatic`.

#### 4. Restart services

```bash
make deploy-restart
```

Restarts migrations (runs migrate + collectstatic), then web + celery.

#### 5. Verify

```bash
make deploy-verify
```

## Common Gotchas

### "Missing staticfiles manifest entry for X" (500 on all pages)

**Cause:** `collectstatic` couldn't find source files in `STATICFILES_DIRS` (`frontend/dist/static/`), so the manifest is incomplete.

**Fix:** Run `make deploy-static` to populate `frontend/dist/static/` and regenerate the manifest.

### Frontend changes don't appear on production

**Cause:** `npm run dist` output wasn't committed. Production serves whatever JS/CSS is in git.

**Fix:**
```bash
make frontend-build
git add static/js/ static/css/ static/staticfiles.json
git commit -m "chore: rebuild frontend"
git push origin main
make deploy
```

### TechniqueMedia records missing (green links don't show)

**Cause:** `TechniqueMedia` is stored in the database, not in `techniques.json`. Local DB associations don't automatically sync to production.

**Fix:**
```bash
make push-technique-media
```

This exports from local DB and imports to production.

### Node.js OpenSSL error during frontend build

**Cause:** Node 17+ changed OpenSSL defaults; this project's webpack 5 uses legacy algorithms.

**Fix:** Already handled in `make frontend-build` via `NODE_OPTIONS=--openssl-legacy-provider`.

## What lives where

| Data | Location | Synced how |
|------|----------|------------|
| Technique tree structure | `files/data/techniques.json` (git) | `git push` + `git pull` |
| Technique-media links | `TechniqueMedia` table (DB) | `make push-technique-media` |
| Built JS/CSS bundles | `static/js/`, `static/css/` (git) | `make frontend-build` + commit |
| Static file manifest | `static/staticfiles.json` (regenerated) | `collectstatic` on server |
| Favicon/image/lib hashes | `frontend/dist/static/` (not in git) | `make deploy-static` copies them |
