# Changelog

## 2026-03-02

- **feat:** Revise Sharing Options — trim to 7 platforms (fb, tw, whatsapp, telegram, reddit, linkedin, email), remove embed/tumblr/vk/pinterest/mix, delete MediaShareEmbed.jsx and optionsEmbedded.js
- **feat:** Remove Embed Page — `embed_media` view, URL, template, `EmbedPage.tsx`, config, renderer
- **feat:** Remove Featured/Recommended Media — views, URLs, Celery task, settings, `featured`/`user_featured` fields, frontend pages/configs
- **feat:** Remove Media Reporting — `reported_times` field, `CAN_REPORT_MEDIA` setting, report action, `ReportForm.jsx`, report config, management table column
- **feat:** Remove Email Functionality — django-celery-email, EMAIL_* settings, notify_users(), email templates, notification toggles
- **feat:** Remove Contact Feature — contact page, contact_user API, allow_contact field, ChannelContactForm, sidebar nav link
- **feat:** Remove Subtitles — `Language`/`Subtitle` models, `SubtitleForm`, `add_subtitle` view/URL/template, frontend components
- **feat:** Remove Member Directory — view, URL, template, MembersPage.tsx, config entries
- **feat:** Remove Notifications + Channel Subscriptions — `Notification` model, `NOTIFICATION_METHODS`, `subscribers` M2M
- **feat:** Remove License model — model, FK on Media, serializer field, migration
- **feat:** Remove RSS feeds — delete feeds.py, URL patterns, head template link, context_processor/view references
- **feat:** Remove ratings system — `RatingCategory`/`Rating` models, `rating_category` M2M, `ratings_info`, `update_user_ratings()`, `rate` action, settings
- **chore(i18n):** Remove dormant i18n infrastructure — `USE_I18N = False`, strip `{% trans %}` / `{% blocktrans %}` from 27 templates, remove `gettext_lazy`
- **chore(dev):** Add local test infrastructure — `docker-compose-test.yaml`, `make test-local` / `check-local` targets, exclude `node_modules` from linters

## 2026-03-01

- **feat(techniques):** Add `/techniques` page — tree view of BJJ technique data
- **data:** Remove "Low X Guard to leg drag" from Guard > Low X Guard
- **data:** Remove empty "Other / Control concepts" subcategory from Guard
- **data:** Add "X-Guard top Leg pummeling with far sleeve control" to Passing > vs X Guard

## 2026-02-28

- **feat(sync):** Add remote DB sync and media proxy for local dev
- **fix(ci):** Update GitHub Actions for local build and modern actions
- **chore:** Local Docker build (`Dockerfile.local`, Python 3.9 / Bullseye)
- **chore:** Dev workflow tooling — Makefile, .editorconfig, .python-version
