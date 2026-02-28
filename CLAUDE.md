# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MediaCMS is an open source video and media CMS built with Django + React. It supports video, audio, image, and PDF uploads with automatic transcoding, HLS adaptive streaming, and a REST API.

## Common Commands

### Docker Development
```bash
# Start full dev environment (Django + frontend + Selenium + DB + Redis)
docker compose -f docker-compose-dev.yaml up --build

# Start production stack
docker compose up

# Run Django management commands inside container
docker compose exec web python manage.py <command>
```

### Django (local or inside container)
```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### Tests
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/api/test_user_login.py

# Run a specific test
pytest tests/api/test_user_login.py::TestUserLogin::test_login

# Run with coverage
pytest --cov
```

Settings module for tests: `DJANGO_SETTINGS_MODULE=cms.settings` (configured in pytest.ini).

### Frontend
```bash
cd frontend
npm install
npm run start    # Dev server on port 8088
npm run dist     # Production build
```

### Linting
```bash
flake8           # Python linting (config in setup.cfg, ignores E501)
black .          # Python formatting (line-length 200, config in pyproject.toml)
```

## Architecture

### Django Apps

- **cms/** - Project configuration: settings, root URL routing, Celery app setup, WSGI/ASGI entry points
- **files/** - Core app: Media model, categories, tags, encoding profiles, playlists, comments, subtitles. Contains the bulk of business logic including FFmpeg-based transcoding, HLS generation, and full-text search via PostgreSQL search vectors
- **users/** - User accounts (extends AbstractUser), channels with subscriptions, roles (advancedUser, editor, manager). Authentication via django-allauth
- **actions/** - Tracks user interactions (like, dislike, watch, report, rate) via a single MediaAction model. Supports anonymous tracking via session keys
- **uploader/** - Chunked file upload handling via Fine Uploader with automatic Media object creation

### Frontend (frontend/)

React 17 app using Flux for state management, built with Webpack 5. Key structure:
- `packages/scripts/` - Custom build tooling (mediacms-scripts)
- `packages/player/` - Custom video player built on Video.js
- `packages/vjs-plugin/` - Video.js plugin extensions
- `config/mediacms.config.js` - Build and page configuration
- `src/` - Application source with page components (Home, Search, Media, Upload, Management)

### Media Processing Pipeline

1. Chunked upload via Fine Uploader → `uploader/` app
2. Media object created, file type detected (video/audio/image/PDF)
3. For video: thumbnail extraction, sprite sheet generation, encoding queued as Celery tasks
4. Multiple encoding profiles applied (240p–2160p, h264/h265/vp9)
5. HLS playlist generated via Bento4 MP4HLS for adaptive streaming
6. Media becomes publicly listable when encoding succeeds and (optionally) reviewed

### Services (Docker Compose)

- **web** - Django app served via uWSGI + Nginx
- **celery_worker** - Processes encoding and other async tasks (short and long queues)
- **celery_beat** - Periodic task scheduler
- **db** - PostgreSQL 13
- **redis** - Cache backend and Celery broker

### REST API

Documented via Swagger at `/swagger/` and ReDoc at `/api/`. Key endpoints under `/api/v1/`:
- `media/`, `media/{token}` - Media CRUD
- `search` - Full-text search
- `playlists/`, `playlists/{token}` - Playlist management
- `comments`, `media/{token}/comments` - Comments
- `users/`, `users/{username}` - User profiles
- `login`, `whoami` - Authentication
- `encode_profiles` - Available encoding profiles
- `manage_media`, `manage_users`, `manage_comments` - Admin management

### Key Configuration (cms/settings.py)

- `PORTAL_WORKFLOW` - Default media visibility: 'public', 'private', 'unlisted'
- `CAN_ADD_MEDIA` - Upload permissions: 'all', 'email_verified', 'advancedUser'
- `MEDIA_IS_REVIEWED` - Whether admin review is required before publishing
- `ALLOW_ANONYMOUS` / `ALLOW_ANONYMOUS_ACTIONS` - Guest access controls
- `DEFAULT_THEME` - 'light' or 'dark'

### External Dependencies

- **FFmpeg/FFprobe** - Media encoding and analysis
- **Bento4 (MP4HLS)** - HLS stream generation
- **ImageMagick** - Image processing
- **PostgreSQL** - Database with full-text search
- **Redis** - Caching and Celery broker
