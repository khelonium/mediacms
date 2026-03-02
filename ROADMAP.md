# Roadmap

## Up Next
<!-- Items in priority order. Move to Done when complete. -->

---

---

---

### Phase D — Third-Party Package Cleanup (after all feature removals)

#### ~~D1. Remove drf-yasg~~ (done)

#### D2. Remove Unused Packages (group into 1 PR)
- `django-ckeditor`: INSTALLED_APPS + `CKEDITOR_CONFIGS` setting + requirements.txt
- `django-debug-toolbar`: INSTALLED_APPS + MIDDLEWARE + `cms/urls.py` import/URL + requirements.txt + `INTERNAL_IPS`
- `django-crispy-forms`: INSTALLED_APPS + requirements.txt

#### D3. Verify django.contrib.sites
- allauth 0.44.0 may require it — test before removing
- If safe: remove from INSTALLED_APPS, remove `SITE_ID`, drop `django_site` table

---

## Execution Order Summary

```
Phase A (parallel, any order):
  A1 Ratings          A2 RSS Feeds       A3 License
  A4 Notifications    A5 Members         A6 Subtitles

Existing items (sequential):
  Contact → Email

Phase B: (all done)

Phase C: (all done)

Phase D (after all features removed):
  D1 drf-yasg         D2 Unused packages    D3 django.contrib.sites
```

## What This Enables

After all phases, the remaining surface area is:
- **Apps:** cms (config), files (Media, Category, Tag, Technique, EncodeProfile, Encoding), users (User, Channel), uploader
- **Models:** ~12 instead of ~18+ (keeping Playlist, PlaylistMedia, MediaAction)
- **Third-party:** Django, DRF, allauth, celery, redis, psycopg2, Pillow, imagekit, mptt, m3u8, filetype
- **Frontend pages:** Home, Search, Latest, Media, Upload, Profile, Categories, Tags, Techniques, Edit Media, Playlists, History

This makes feasible:
1. **Django 4.x/5.x upgrade** — fewer package compatibility blockers
2. **Framework migration** — ~12 API endpoints instead of ~25+, clearer separation of media pipeline (Celery+FFmpeg) from web layer
3. **Frontend modernization** — React 17+Flux → React 18+ or alternative, with fewer pages to port
4. **Test coverage** — smaller codebase makes comprehensive testing tractable

---

## Done
<!-- Completed items are recorded in docs/changelog.md -->

### D1. Remove drf-yasg
- Removed `drf-yasg` from requirements.txt and `drf_yasg` from INSTALLED_APPS. Removed `schema_view` definition and `/swagger/`, `/docs/api/` URL patterns from `cms/urls.py`. Stripped all `@swagger_auto_schema` decorators (28 total) and `openapi` imports from `files/views.py` and `users/views.py`.

### C1. Simplify Actions App
- Stripped `MediaAction` model to watch-only: removed `action`, `extra_info` fields, `USER_MEDIA_ACTIONS` choices tuple. Simplified `save_user_action` task (flattened watch-specific branches, removed action/extra_info params). Rewrote `pre_save_action` (removed action param, clearer throttling logic). Hardcoded `action="watch"` in `MediaActions`/`UserActions` views. Removed dead `actions`/`members` frontend API config entries. Migration drops columns.

### B5. Remove Management Pages
- Deleted `management_views.py` (manage media/users API views), `manage_media`/`manage_users` Django views, `/manage/media` and `/manage/users` URL patterns, `/api/v1/manage_media` and `/api/v1/manage_users` API endpoints, `manage_media.html`/`manage_users.html` templates. Deleted `ManageMediaPage.js`/`ManageUsersPage.js`, entire `management-table/` component directory, `useManagementTableHeader` hook, `formatManagementTableDate` helper. Removed management nav items from sidebar, manage URL/API/permission configs from templates. Cleaned up stale featured/recommended URL entries.

### B4. Revise Sharing Options
- Trimmed `shareOptions` from 12 to 7: removed embed (page deleted in B3), tumblr, vk, pinterest, mix (defunct). Kept: fb, tw, whatsapp, telegram, reddit, linkedin, email. Deleted `MediaShareEmbed.jsx`, `optionsEmbedded.js`, embed share UI code, `embeddedVideo` config. Simplified `MediaShareButton` (no longer needs video/non-video page distinction). Cleaned up stale featured/recommended URL refs in config.js.

### B3. Remove Embed Page
- Removed `embed_media` view, `/embed` URL pattern, `embed.html` template, `EmbedPage.tsx`, embed page config, `renderEmbedPage` renderer, EJS templates. Cleaned up stale page exports (`MembersPage`, `FeaturedMediaPage`, `RecommendedMediaPage`) from `index.ts`.

### B2. Remove Featured/Recommended Media
- Removed `featured`/`user_featured` fields on Media, `featured_media`/`recommended_media` views, `/featured`/`/popular`/`/recommended` URL patterns, `show_recommended_media()`, `get_list_of_popular_media` Celery beat task, `VIDEO_PLAYER_FEATURED_VIDEO_ON_INDEX_PAGE` setting, `FeaturedMediaPage.tsx`/`RecommendedMediaPage.tsx`, featured/recommended sections from HomePage, sidebar nav items, management table column, admin filters, serializer/form fields. Migration drops columns.

### B1. Remove Media Reporting
- Removed `reported_times` field, `CAN_REPORT_MEDIA`/`REPORTED_TIMES_THRESHOLD` settings, `report` action from `USER_MEDIA_ACTIONS`, report handling in `pre_save_action`/`save_user_action`/`MediaActions` view, `CAN_REPORT_MEDIA` context var, `ReportForm.jsx`, report config in features template/config, `reportMedia` member permission, `MediaPageStore` report methods, management table reported column. Migration drops column.

### Remove Email Functionality
- Removed `django-celery-email` package and `djcelery_email` from INSTALLED_APPS, all `EMAIL_*` settings, `ADMIN_EMAIL_LIST`, `USERS_NOTIFICATIONS`/`ADMINS_NOTIFICATIONS`, `notify_users()`, new-user email alert signal. Stubbed allauth adapter `send_mail`. Set `ACCOUNT_EMAIL_VERIFICATION = "none"`. Deleted email templates.

### Remove Contact Feature
- Removed `/contact` page view/form/URL/template, user-to-user `contact_user` API endpoint, `allow_contact` field on User model, `SHOW_CONTACT_FORM` context, `ChannelContactForm` React component, sidebar nav link, `contactUser` permission, profile contact form SCSS. Migration drops column.

### A6. Remove Subtitles
- Removed `Language` + `Subtitle` models, `SubtitleForm`, `add_subtitle` view/URL/template, `subtitles_info`/`add_subtitle_url` properties, admin registrations, serializer fields, `SUBTITLES_UPLOAD_DIR` setting, frontend subtitle components. Migration drops tables.

### A5. Remove Member Directory
- Removed `members` view, URL, template, `MembersPage.tsx`, all page/URL/API config entries. Redirects changed to `/`.

### A4. Remove Notifications + Channel Subscriptions
- Removed `Notification` model, `NOTIFICATION_METHODS`, `subscribers` M2M on Channel. Migration drops tables.

### A3. Remove License Model
- Removed `License` model, `license` FK on Media, serializer field. Migration drops table and column.

### A2. Remove RSS Feeds
- Deleted `files/feeds.py`, removed feed URL patterns, RSS `<link>` from head template, `RSS_URL` from context_processors and search view.

### A1. Remove Ratings System
- Removed `RatingCategory` + `Rating` models, `rating_category` M2M on Media, `ratings_info` property, `update_user_ratings()`, `rate` action, `ALLOW_RATINGS` settings, serializer/view/context_processor references. Migration to drop tables.

### Remove Like/Dislike Functionality
- Removed Like/Dislike from models, API endpoints, Celery tasks, serializers, React components, navigation, pages, state management, config, templates. Database migration to drop `likes`/`dislikes` columns.
- **Commit:** `350fa47`
