# Progress

## Current Focus

Local development environment setup and workflow tooling.

## Completed

| Date       | Item                                          | Notes                                                  |
|------------|-----------------------------------------------|--------------------------------------------------------|
| 2026-02-28 | Local Docker build (`Dockerfile.local`)       | Python 3.9 / Bullseye; replaces Docker Hub pull        |
| 2026-02-28 | `docker-compose.yaml` updated for local build | All services use `mediacms/mediacms:local` image        |
| 2026-02-28 | Dev workflow tooling                          | Makefile, .editorconfig, .python-version, CI fixes     |
| 2026-02-28 | Decision log (`MEMORY.md`)                    | Docker, allauth middleware, black line-length decisions |

## Upcoming

- Explore media upload + transcoding pipeline end-to-end
- Review and customize `cms/settings.py` for local development
- Frontend development setup (`frontend/` React app)
