# Roadmap

## Up Next
<!-- Items in priority order. Move to Done when complete. -->

---

### Phase A — Quick Wins (trivial, no cross-dependencies)

Phase A items can be done in any order.

#### A1. Remove Ratings System
- **Why:** `ALLOW_RATINGS=False` — entirely dead code
- **Scope:** `RatingCategory` + `Rating` models, `rating_category` M2M on Media, `ratings_info` property, `update_user_ratings()`, `rate` action in actions/models.py, settings, serializer fields
- **Files:** `files/models.py`, `files/methods.py`, `files/tasks.py`, `files/serializers.py`, `files/views.py`, `actions/models.py`, `cms/settings.py`
- **Migration:** Drop `files_ratingcategory`, `files_rating`, `files_media_rating_category`

#### A2. Remove RSS Feeds
- **Why:** Legacy distribution channel, no consumers
- **Scope:** Delete `files/feeds.py`, remove feed URL patterns, remove `RSS_URL` from context_processors
- **Files:** `files/feeds.py` (delete), `files/urls.py`, `files/context_processors.py`

#### A3. Remove License Model
- **Why:** Never populated or exposed in UI
- **Scope:** `License` model, `license` FK on Media, serializer field
- **Files:** `files/models.py`, `files/serializers.py`
- **Migration:** Drop `files_license`, drop `license_id` from `files_media`

#### A4. Remove Notifications + Channel Subscriptions
- **Why:** `Notification` model is dead code; `subscribers` M2M on Channel has no UI/API
- **Scope:** `Notification` model, `NOTIFICATION_METHODS`, `subscribers` M2M on Channel
- **Files:** `users/models.py`
- **Migration:** Drop `users_notification`, `users_channel_subscribers`
- **Note:** Leave `USERS_NOTIFICATIONS`/`ADMINS_NOTIFICATIONS` settings — removed later with Email item

#### A5. Remove Member Directory
- **Why:** Public user listing not needed for private portal
- **Scope:** `members` view, URL, template, `MembersPage.tsx`, page config entries
- **Files:** `files/views.py`, `files/urls.py`, `templates/cms/members.html` (delete), `frontend/src/.../MembersPage.tsx`

#### A6. Remove Subtitles
- **Why:** Not needed for this use case
- **Scope:** `Subtitle` + `Language` models, `SubtitleForm`, `add_subtitle` view/URL/template, `subtitles_info` property on Media, admin registrations
- **Files:** `files/models.py`, `files/forms.py`, `files/views.py`, `files/urls.py`, `files/admin.py`, `templates/cms/add_subtitle.html` (delete)
- **Migration:** Drop `files_subtitle`, `files_language`

---

### Existing Items (sequential: Contact before Email)

#### Remove Contact Feature
- **Why:** Unused feature — no contact page linked in the main UI, user-to-user messaging not needed for this use case
- **Scope:** Remove `/contact` page (view, form, URL, template), user-to-user contact API endpoint, `allow_contact` field on User model, `ChannelContactForm` React component, sidebar nav link, profile page contact form logic, related SCSS. Database migration to drop `allow_contact` column.
- **Files (~20):**
  - **Backend:** `files/views.py` (contact view), `files/forms.py` (ContactForm), `files/urls.py` (contact URL), `users/views.py` (contact_user endpoint + SHOW_CONTACT_FORM context), `users/urls.py` (contact_user URL), `users/models.py` (allow_contact field), `users/forms.py` (commented allow_contact)
  - **Templates:** `templates/cms/contact.html` (delete), `templates/config/installation/contents.html` (nav link), `templates/cms/add-media.html` (contact link in help text)
  - **Frontend:** `frontend/src/.../ProfileAboutPage.js` (ChannelContactForm + enabledContactForm), `frontend/src/.../ProfilePagesContent.js` (with-cform class), `frontend/src/.../member.js` (contactUser permission), `frontend/src/.../user.config.js` (contactUser default), `frontend/src/.../contents.config.js` (nav link), `frontend/src/.../ProfilePage.scss` (contact form styles), `frontend/config/templates/static/contactPage.html` (delete), `frontend/config/mediacms.config.templates.js` (contactPage entry)
  - **Tests:** `tests/forms/test_contact_TOWRITE.py` (delete placeholder)
  - **Migration:** New migration to drop `allow_contact` column from `users_user`

#### Remove Email Functionality
- **Why:** Simplify operations — remove SMTP dependency, async email infrastructure, notification system
- **Depends on:** Remove Contact Feature (contact form sends email — remove that first to reduce scope)
- **Scope:** Remove `django-celery-email` package and `djcelery_email` from INSTALLED_APPS, all `EMAIL_*` settings, `ADMIN_EMAIL_LIST`, notification toggle settings (`USERS_NOTIFICATIONS`, `ADMINS_NOTIFICATIONS`). Stub out allauth email adapter (`users/adapter.py`), remove `notify_users()` email logic in `files/methods.py`, remove new-user email alert signal in `users/models.py`. Set `ACCOUNT_EMAIL_VERIFICATION = "none"` so signup works without SMTP. Remove email templates.
- **Files (~15):**
  - **Backend:** `cms/settings.py` (EMAIL_* settings, INSTALLED_APPS, notification toggles), `users/adapter.py` (stub send_mail), `users/models.py` (post_user_create signal email block), `files/methods.py` (notify_users email logic)
  - **Config:** `requirements.txt` (django-celery-email)
  - **Templates:** `templates/account/email/` (4 email body/subject templates), `templates/account/email.html` (email management page), `templates/account/messages/` (email-related flash messages)

---

### Phase B — Feature Removals (moderate complexity, need migrations)

Phase B items can be done in parallel except B1 must complete before Phase C.

#### B1. Remove Media Reporting
- **Why:** Django admin suffices for moderation
- **Scope:** `reported_times` field, `CAN_REPORT_MEDIA` setting, `report` action handling in tasks/views/methods, `ReportForm.jsx`, report in features config
- **Files:** `files/models.py`, `files/views.py`, `files/tasks.py`, `files/methods.py`, `files/serializers.py`, `files/management_views.py`, `files/forms.py`, `actions/models.py`, `cms/settings.py`, `frontend/src/.../ReportForm.jsx` (delete), `frontend/src/.../features.config.js`
- **Migration:** Drop `reported_times` from `files_media`
- **Note:** Must complete before C1

#### B2. Remove Featured/Recommended Media
- **Why:** Simple "latest" listing suffices; editorial features add complexity
- **Scope:** `featured_media`/`recommended_media` views, URLs, templates, `show_recommended_media()`, `get_list_of_popular_media` Celery beat task, `VIDEO_PLAYER_FEATURED_VIDEO_ON_INDEX_PAGE` setting, `featured`/`user_featured` fields on Media, `FeaturedMediaPage.tsx`, `RecommendedMediaPage.tsx`
- **Files:** `files/views.py`, `files/urls.py`, `files/methods.py`, `files/tasks.py`, `files/models.py`, `files/serializers.py`, `files/forms.py`, `cms/settings.py`
- **Migration:** Drop `featured`, `user_featured` from `files_media`

#### B3. Remove Embed Page
- **Why:** Embed is an external integration point; sharing options are kept but embed view is separate
- **Scope:** `embed_media` view, embed URL/template, `EmbedPage.tsx`
- **Files:** `files/views.py`, `files/urls.py`, `templates/cms/embed.html` (delete)

#### B4. Revise Sharing Options
- **Why:** Current config has 13 share targets (fb, tw, whatsapp, telegram, reddit, tumblr, vk, pinterest, mix, linkedin, email, embed). Trim to only relevant ones.
- **Scope:** Update `shareOptions` in `frontend/src/templates/config/installation/features.config.js`
- **Note:** Config change only, not a code removal. Decide specific platforms later.

#### B5. Remove Management Pages
- **Why:** Django admin suffices for media/user management
- **Scope:** `manage_media`/`manage_users` views, `management_views.py` API views, URLs, templates, `ManageMediaPage.js`, `ManageUsersPage.js`
- **Files:** `files/views.py`, `files/management_views.py`, `files/urls.py`, `templates/cms/manage_media.html` (delete), `templates/cms/manage_users.html` (delete)

---

### Phase C — App-Level Simplification (after A1 + B1)

#### C1. Simplify Actions App
- **Why:** After removing like (done), report (B1), and rate (A1), only `watch` action remains. History and playlists are kept.
- **Depends on:** A1 (Ratings) + B1 (Reporting) must be done first
- **Scope:** Strip `MediaAction` to `watch` only, remove `report`/`rate` choices, clean up `save_user_action` task to remove report/rate handling
- **Note:** Keep simplified app — `watch` action powers both view-count and history features

---

### Phase D — Third-Party Package Cleanup (after all feature removals)

#### D1. Remove drf-yasg (Swagger/API docs)
- **Scope:** Remove from INSTALLED_APPS, requirements.txt, `cms/urls.py` schema_view + swagger/redoc URLs, all `@swagger_auto_schema` decorators and `openapi` imports across `files/views.py`, `files/management_views.py`, `users/views.py`
- **Note:** Moderate — many files have decorators

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

Phase B (mostly parallel, B1 before C1):
  B1 Reporting              B2 Featured/Recommended
  B3 Remove Embed Page      B4 Revise Sharing Options (config only)
  B5 Management Pages

Phase C (after A1 + B1):
  C1 Simplify Actions App

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

### Remove Like/Dislike Functionality
- Removed Like/Dislike from models, API endpoints, Celery tasks, serializers, React components, navigation, pages, state management, config, templates. Database migration to drop `likes`/`dislikes` columns.
- **Commit:** `350fa47`
