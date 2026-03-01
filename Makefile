.DEFAULT_GOAL := help
COMPOSE := docker compose

# ──────────────────────────────────────────────
# Docker lifecycle
# ──────────────────────────────────────────────

.PHONY: up down rebuild logs

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

rebuild: ## Rebuild images and restart
	$(COMPOSE) up -d --build

logs: ## Tail logs (all services)
	$(COMPOSE) logs -f

# ──────────────────────────────────────────────
# Django management (runs inside web container)
# ──────────────────────────────────────────────

.PHONY: shell dbshell migrate makemigrations createsuperuser collectstatic

shell: ## Open Django shell
	$(COMPOSE) exec web python manage.py shell

dbshell: ## Open database shell
	$(COMPOSE) exec db psql -U mediacms mediacms

migrate: ## Run Django migrations
	$(COMPOSE) exec web python manage.py migrate

makemigrations: ## Create new migrations
	$(COMPOSE) exec web python manage.py makemigrations

createsuperuser: ## Create admin superuser
	$(COMPOSE) exec web python manage.py createsuperuser

collectstatic: ## Collect static files
	$(COMPOSE) exec web python manage.py collectstatic --noinput

# ──────────────────────────────────────────────
# Quality gates
# ──────────────────────────────────────────────

.PHONY: test lint format format-check check

test: ## Run pytest inside web container
	$(COMPOSE) exec -e TESTING=True web pytest

lint: ## Run flake8 inside web container
	$(COMPOSE) exec web flake8

format: ## Run black (auto-fix) inside web container
	$(COMPOSE) exec web black .

format-check: ## Check formatting without changing files
	$(COMPOSE) exec web black --check .

check: lint format-check test ## Run all quality gates (lint + format-check + test)

# ──────────────────────────────────────────────
# Remote sync (mirror bjj.chadao.ro content)
# ──────────────────────────────────────────────

REMOTE_HOST ?= bjj.chadao.ro
REMOTE_USER ?= root
REMOTE_DIR  ?= /mediacms/cms/mediacms
REMOTE_COMPOSE ?= docker-compose-letsencrypt.yaml

.PHONY: sync-db sync-assets sync-json sync-remote

sync-db: ## Dump remote DB and restore locally
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T db pg_dump -U mediacms -Fc mediacms" > bjj_dump.pgdump
	$(COMPOSE) exec -T db pg_restore -U mediacms -d mediacms --clean --if-exists < bjj_dump.pgdump
	@echo "Database restored. Run 'make migrate' if needed."

sync-assets: ## Download thumbnails + HLS manifests from remote
	$(COMPOSE) exec web python manage.py sync_remote_assets

sync-json: ## Sync techniques.json from remote server
	ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T web cat files/data/techniques.json" > files/data/techniques.json
	@echo "techniques.json synced from $(REMOTE_HOST)"

sync-remote: sync-db sync-assets sync-json ## Full sync: database + assets + JSON data from remote

# ──────────────────────────────────────────────
# Frontend build
# ──────────────────────────────────────────────

.PHONY: frontend-build

frontend-build: ## Rebuild frontend and copy to static/
	cd frontend && NODE_OPTIONS=--openssl-legacy-provider npm run dist
	cp frontend/dist/static/js/*.js static/js/
	cp frontend/dist/static/js/*.txt static/js/ 2>/dev/null || true
	cp frontend/dist/static/css/*.css static/css/
	@echo "Frontend built and copied to static/"

# ──────────────────────────────────────────────
# Deploy to production (stop-migrate-start)
# ──────────────────────────────────────────────

REMOTE := $(REMOTE_USER)@$(REMOTE_HOST)
REMOTE_CD := cd $(REMOTE_DIR)
REMOTE_DC := docker compose -f $(REMOTE_COMPOSE)

.PHONY: deploy deploy-pre-check deploy-db-backup deploy-backup deploy-pull deploy-static deploy-migrate deploy-restart deploy-verify deploy-rollback

deploy: deploy-pre-check deploy-db-backup deploy-backup deploy-pull deploy-static deploy-migrate deploy-restart deploy-verify ## Full deploy to production

deploy-pre-check: ## Validate local state before deploying
	@echo "=== Pre-deploy checks ==="
	@test "$$(git branch --show-current)" = "main" || (echo "ERROR: not on main branch" && exit 1)
	@test -z "$$(git status --porcelain)" || (echo "ERROR: working tree not clean" && exit 1)
	@git fetch origin main --quiet
	@test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" || (echo "ERROR: local main not pushed to origin" && exit 1)
	@test -d frontend/dist/static || (echo "ERROR: frontend/dist/static/ does not exist — run make frontend-build" && exit 1)
	@git ls-files --error-unmatch static/staticfiles.json >/dev/null 2>&1 || (echo "ERROR: static/staticfiles.json not tracked in git" && exit 1)
	@echo "All pre-deploy checks passed."

deploy-db-backup: ## Dump production database before deploy
	@echo "=== Backing up production database ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) exec -T db pg_dump -U mediacms -Fc mediacms" > pre-deploy-$$(date +%Y%m%d-%H%M%S).pgdump
	@echo "Database backup saved to pre-deploy-*.pgdump"

deploy-backup: ## Record current production commit for rollback
	@echo "=== Recording rollback commit ==="
	ssh $(REMOTE) "$(REMOTE_CD) && git rev-parse HEAD" > .deploy-rollback-commit
	@echo "Rollback commit: $$(cat .deploy-rollback-commit)"

deploy-pull: ## Pull latest code on production
	ssh $(REMOTE) "$(REMOTE_CD) && git pull origin main"

deploy-static: ## Ensure frontend/dist/static exists and run collectstatic on production
	ssh $(REMOTE) "$(REMOTE_CD) && mkdir -p frontend/dist/static && cp -r static/js static/css static/favicons static/images static/lib frontend/dist/static/"
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) exec -T web python manage.py collectstatic --noinput"

deploy-migrate: ## Stop services, run migrations, validate manifest
	@echo "=== Stopping web + celery ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) stop web celery_worker celery_beat"
	@echo "=== Running migrations ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) run --rm migrations ./deploy/docker/prestart.sh"
	@echo "Migrations complete."

deploy-restart: ## Start services and poll for HTTP 200
	@echo "=== Starting services ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) start web celery_worker celery_beat"
	@echo "Waiting for HTTP 200..."
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
		code=$$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 5 https://$(REMOTE_HOST)/ 2>/dev/null); \
		if [ "$$code" = "200" ]; then echo "Homepage returned 200 after $$i attempts"; break; fi; \
		if [ "$$i" = "15" ]; then echo "ERROR: homepage not returning 200 after 15 attempts (last: $$code)" && exit 1; fi; \
		sleep 2; \
	done

deploy-verify: ## Comprehensive health check after deploy
	@echo "=== Git state ==="
	ssh $(REMOTE) "$(REMOTE_CD) && git log --oneline -1"
	@echo ""
	@echo "=== Migration status (files) ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) exec -T web python manage.py showmigrations files"
	@echo ""
	@echo "=== Migration status (users) ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) exec -T web python manage.py showmigrations users"
	@echo ""
	@echo "=== Container status ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) ps"
	@echo ""
	@echo "=== HTTP checks ==="
	@curl -s -o /dev/null -w "Homepage:   %{http_code}\n" -L https://$(REMOTE_HOST)/
	@curl -s -o /dev/null -w "API:        %{http_code}\n" -L https://$(REMOTE_HOST)/api/v1/
	@curl -s -o /dev/null -w "Techniques: %{http_code}\n" -L https://$(REMOTE_HOST)/techniques/
	@echo ""
	@echo "=== Manifest entry count ==="
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) exec -T web python -c \"import json; m=json.load(open('static/staticfiles.json')); print(len(m.get('paths', {})), 'entries')\""
	@echo ""
	@echo "Deploy complete."

deploy-rollback: ## Rollback to pre-deploy commit
	@test -f .deploy-rollback-commit || (echo "ERROR: no .deploy-rollback-commit file found" && exit 1)
	@echo "=== Rolling back to $$(cat .deploy-rollback-commit) ==="
	ssh $(REMOTE) "$(REMOTE_CD) && git checkout $$(cat .deploy-rollback-commit)"
	ssh $(REMOTE) "$(REMOTE_CD) && mkdir -p frontend/dist/static && cp -r static/js static/css static/favicons static/images static/lib frontend/dist/static/"
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) exec -T web python manage.py collectstatic --noinput"
	ssh $(REMOTE) "$(REMOTE_CD) && $(REMOTE_DC) restart web celery_worker celery_beat"
	@echo "Rollback complete. Verify with: make deploy-verify"

# ──────────────────────────────────────────────
# Sync DB data to production
# ──────────────────────────────────────────────

.PHONY: push-technique-media rebuild-techniques

push-technique-media: ## Export local TechniqueMedia records and import to production
	@echo "Exporting TechniqueMedia from local DB..."
	$(COMPOSE) exec -T web python manage.py shell -c "\
from files.models import TechniqueMedia; \
[print(f'{tm.technique.slug}|{tm.media.friendly_token}|{tm.title_override or \"\"}') for tm in TechniqueMedia.objects.select_related('technique', 'media').all()]" > /tmp/technique_media_export.txt
	@echo "Importing $$(wc -l < /tmp/technique_media_export.txt | tr -d ' ') records to production..."
	@cat /tmp/technique_media_export.txt | ssh $(REMOTE_USER)@$(REMOTE_HOST) "cd $(REMOTE_DIR) && docker-compose -f $(REMOTE_COMPOSE) exec -T web python manage.py shell -c \"\
import sys; \
from files.models import Technique, TechniqueMedia, Media; \
from users.models import User; \
admin = User.objects.filter(is_superuser=True).first(); \
created = 0; \
for line in sys.stdin: \
    parts = line.strip().split('|'); \
    if len(parts) < 2: continue; \
    slug, token, title = parts[0], parts[1], parts[2] if len(parts) > 2 else ''; \
    try: \
        technique = Technique.objects.get(slug=slug); \
        media = Media.objects.get(friendly_token=token); \
        _, was_created = TechniqueMedia.objects.get_or_create(technique=technique, media=media, defaults={'title_override': title, 'added_by': admin}); \
        created += int(was_created); \
    except (Technique.DoesNotExist, Media.DoesNotExist) as e: print('Missing: ' + slug + '/' + token); \
print(str(created) + ' records created'); \
\""
	@rm /tmp/technique_media_export.txt

rebuild-techniques: ## Rebuild MPTT tree for Technique model
	$(COMPOSE) exec web python manage.py shell -c "from files.models import Technique; Technique.objects.rebuild(); print(f'Rebuilt {Technique.objects.count()} techniques')"

# ──────────────────────────────────────────────
# Status
# ──────────────────────────────────────────────

.PHONY: status

status: ## Show running containers and URLs
	@echo "=== Running containers ==="
	@$(COMPOSE) ps
	@echo ""
	@echo "=== URLs ==="
	@echo "  Web:     http://localhost"
	@echo "  API:     http://localhost/api/v1/"
	@echo "  Swagger: http://localhost/swagger/"
	@echo "  Admin:   http://localhost/admin/"

# ──────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────

.PHONY: help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
