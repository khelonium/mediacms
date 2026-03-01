# Deploy to Production

## Instructions

Deploy the current `main` branch to production. Follow these steps in order, stopping on any failure.

### 1. Pre-deploy: push to main

Run `git status` and verify:
- Working tree is clean (no uncommitted changes)
- Currently on the `main` branch

If either check fails, **stop and tell the user** what needs to be fixed. Do not proceed.

If clean, run `git push origin main`.

### 2. Deploy: run `make deploy`

Run `make deploy`. This executes the full chain:

`deploy-pre-check` → `deploy-db-backup` → `deploy-backup` → `deploy-pull` → `deploy-static` → `deploy-migrate` → `deploy-restart` → `deploy-verify`

Stream the output to the user. This command can take a few minutes — use a timeout of 600000ms.

### 3. Post-deploy: report results

Summarize the `deploy-verify` output for the user:
- Git SHA deployed
- Migration status
- HTTP health checks (homepage, API, techniques)
- Container status

If **any step failed**, tell the user:
- Run `make deploy-rollback` to roll back to the previous commit
- See `docs/deploy-guide.md` for rollback procedures (including database rollback), common gotchas, and troubleshooting

## Reference

Full deploy documentation, rollback procedures, and troubleshooting: `docs/deploy-guide.md`