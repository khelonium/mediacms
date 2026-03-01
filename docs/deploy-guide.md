# Deploy Guide

Production: `bjj.chadao.ro` | User: `root` | Dir: `/mediacms/cms/mediacms`

## Architecture

Production uses `docker-compose-letsencrypt.yaml` with **volume mounts** (`./:/home/mediacms.io/mediacms/`). This means:
- Code changes take effect after `git pull` + container restart (no image rebuild needed)
- `prestart.sh` runs `migrate` + `collectstatic` on the `migrations` container start
- The web container serves whatever is in `static/` via uWSGI + Nginx

## Deploy Strategy: Stop-Migrate-Start

The deploy sequence explicitly **stops web before migrating**, then starts web after migrations complete. This prevents race conditions where web serves against a partially-migrated schema.

Brief downtime (10-30s) is expected and preferable to 500 errors.

## Deploy Checklist

### Quick deploy

```bash
make deploy
```

This runs: `deploy-pre-check` → `deploy-db-backup` → `deploy-backup` → `deploy-pull` → `deploy-static` → `deploy-migrate` → `deploy-restart` → `deploy-verify`

### Step-by-step (recommended for first use or troubleshooting)

#### 0. Build frontend (if frontend changed)

The Dockerfile does **NOT** run `npm run dist`. Built JS/CSS must be committed.

```bash
make frontend-build       # builds + copies to static/
git add static/js/ static/css/
git commit -m "chore: rebuild frontend"
git push origin main
```

#### 1. Pre-flight checks

```bash
make deploy-pre-check
```

Validates: on main branch, clean working tree, pushed to origin, `frontend/dist/static/` exists, `staticfiles.json` tracked.

#### 2. Database backup

```bash
make deploy-db-backup
```

Creates a `pg_dump -Fc` backup locally as `pre-deploy-YYYYMMDD-HHMMSS.pgdump`. **Critical before destructive migrations** (e.g., DROP TABLE).

#### 3. Record rollback commit

```bash
make deploy-backup
```

Saves the current production commit SHA to `.deploy-rollback-commit`.

#### 4. Pull code

```bash
make deploy-pull
```

#### 5. Populate static files

```bash
make deploy-static
```

Creates `frontend/dist/static/` on the server and copies all static assets there, then runs `collectstatic`.

#### 6. Stop services + run migrations

```bash
make deploy-migrate
```

Stops web/celery/beat, then runs `docker compose run --rm migrations ./deploy/docker/prestart.sh`. This is synchronous — it returns only after migrations and collectstatic complete (or exits non-zero on failure). The manifest is validated (must have >10 entries).

#### 7. Start services

```bash
make deploy-restart
```

Starts web/celery/beat and polls the homepage until HTTP 200 (up to 15 attempts, 2s apart).

#### 8. Verify

```bash
make deploy-verify
```

Checks: git state, migration status (files + users apps), container status, HTTP codes (homepage + API + techniques), manifest entry count.

## Rollback

### Code-only rollback

```bash
make deploy-rollback
```

Checks out the saved commit, re-populates static files, runs collectstatic, and restarts services.

### Database rollback (after destructive migration)

If a destructive migration (e.g., DROP TABLE) broke the database:

```bash
# Restore the database from backup
ssh root@bjj.chadao.ro "cd /mediacms/cms/mediacms && docker compose -f docker-compose-letsencrypt.yaml exec -T db pg_restore -U mediacms -d mediacms --clean --if-exists" < pre-deploy-YYYYMMDD-HHMMSS.pgdump

# Then rollback the code
make deploy-rollback
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

## Django Migration Pitfalls (production environment)

Production runs Python 3.8 / Django 3.x. These issues were discovered deploying the techniques-to-DB migration (0005–0007).

### FK column name collision with existing CharField

**Problem:** Adding a `technique` ForeignKey creates a DB column `technique_id`, which collides with an existing `technique_id` CharField.

**Fix:** Name the temporary FK `technique_fk` (creates column `technique_fk_id`). After removing the old CharField, use `RenameField` to rename `technique_fk` → `technique`.

### MPTT `rebuild()` unavailable in data migrations

**Problem:** `apps.get_model()` returns a historical model with a plain `Manager`, not MPTT's `TreeManager`. Calling `Technique.objects.rebuild()` fails with `AttributeError: 'Manager' object has no attribute 'rebuild'`.

**Fix:** Compute MPTT `lft`/`rght`/`tree_id`/`level` values inline during recursive node creation using nested set numbering instead of relying on `rebuild()`.

### `AlterUniqueTogether` must run before `RemoveField`

**Problem:** `RemoveField` on a column that's part of a `unique_together` constraint causes PostgreSQL to auto-drop the constraint. A later `AlterUniqueTogether` then fails with `Found wrong number (0) of constraints`.

**Fix:** Reorder operations: first `AlterUniqueTogether(unique_together=set())` to explicitly drop the old constraint, then `RemoveField`, then set the new `AlterUniqueTogether`.

## What lives where

| Data | Location | Synced how |
|------|----------|------------|
| Technique tree structure | `Technique` table (DB), seeded from `files/data/techniques.json` | Migration 0006 (initial seed); edit via Django admin |
| Technique-media links | `TechniqueMedia` table (DB) | `make push-technique-media` |
| Built JS/CSS bundles | `static/js/`, `static/css/` (git) | `make frontend-build` + commit |
| Static file manifest | `static/staticfiles.json` (regenerated) | `collectstatic` on server |
| Favicon/image/lib hashes | `frontend/dist/static/` (not in git) | `make deploy-static` copies them |
