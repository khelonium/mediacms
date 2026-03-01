# Progress

## Current Focus

Platform simplification — removing unused features. See [ROADMAP.md](../ROADMAP.md) for details.

## Completed

| Date       | Item                                          | Notes                                                  |
|------------|-----------------------------------------------|--------------------------------------------------------|
| 2026-02-28 | Local Docker build (`Dockerfile.local`)       | Python 3.9 / Bullseye; replaces Docker Hub pull        |
| 2026-02-28 | `docker-compose.yaml` updated for local build | All services use `mediacms/mediacms:local` image        |
| 2026-02-28 | Dev workflow tooling                          | Makefile, .editorconfig, .python-version, CI fixes     |
| 2026-03-01 | Remove social accounts                        | Removed `allauth.socialaccount` from INSTALLED_APPS, switched URL include to `allauth.account.urls`, migration to drop tables |
| 2026-02-28 | Decision log (`MEMORY.md`)                    | Docker, allauth middleware, black line-length decisions |

## Upcoming

See [ROADMAP.md](../ROADMAP.md)
