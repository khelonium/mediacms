# Roadmap

## Up Next
<!-- Items in priority order. Move to changelog when done. -->

### Remove Like Functionality
- **Why:** Simplify the platform — likes/dislikes add complexity without business value for this use case
- **Scope:** Remove Like/Dislike from models, API endpoints, Celery tasks, serializers, React components, navigation, pages, state management, config, templates. Database migration to drop `likes`/`dislikes` columns.
- **Files (~25-30):** `actions/models.py`, `files/models.py`, `files/views.py`, `files/urls.py`, `files/tasks.py`, `files/methods.py`, `files/serializers.py`, `files/management_views.py`, `cms/settings.py`, `frontend/src/.../MediaLikeIcon.jsx`, `frontend/src/.../MediaDislikeIcon.jsx`, `frontend/src/.../ProfileLikedPage.js`, `frontend/src/.../LikedMediaPage.tsx`, `frontend/src/.../MediaPageStore.js`, `frontend/src/.../MediaPageActions.js`, `frontend/src/.../SidebarNavigationMenu.jsx`, `frontend/src/.../member.js`, `frontend/src/.../pages.js`, `frontend/src/.../api.js`, templates

### Remove Contact Feature
- **Why:** Unused feature — no contact page linked in the main UI, user-to-user messaging not needed for this use case
- **Scope:** Remove `/contact` page (view, form, URL, template), user-to-user contact API endpoint, `allow_contact` field on User model, `ChannelContactForm` React component, sidebar nav link, profile page contact form logic, related SCSS. Database migration to drop `allow_contact` column.
- **Files (~20):**
  - **Backend:** `files/views.py` (contact view), `files/forms.py` (ContactForm), `files/urls.py` (contact URL), `users/views.py` (contact_user endpoint + SHOW_CONTACT_FORM context), `users/urls.py` (contact_user URL), `users/models.py` (allow_contact field), `users/forms.py` (commented allow_contact)
  - **Templates:** `templates/cms/contact.html` (delete), `templates/config/installation/contents.html` (nav link), `templates/cms/add-media.html` (contact link in help text)
  - **Frontend:** `frontend/src/.../ProfileAboutPage.js` (ChannelContactForm + enabledContactForm), `frontend/src/.../ProfilePagesContent.js` (with-cform class), `frontend/src/.../member.js` (contactUser permission), `frontend/src/.../user.config.js` (contactUser default), `frontend/src/.../contents.config.js` (nav link), `frontend/src/.../ProfilePage.scss` (contact form styles), `frontend/config/templates/static/contactPage.html` (delete), `frontend/config/mediacms.config.templates.js` (contactPage entry)
  - **Tests:** `tests/forms/test_contact_TOWRITE.py` (delete placeholder)
  - **Migration:** New migration to drop `allow_contact` column from `users_user`

### Remove Email Functionality
- **Why:** Simplify operations — remove SMTP dependency, async email infrastructure, notification system
- **Scope:** Remove `django-celery-email` package and `djcelery_email` from INSTALLED_APPS, all `EMAIL_*` settings, `ADMIN_EMAIL_LIST`, notification toggle settings (`USERS_NOTIFICATIONS`, `ADMINS_NOTIFICATIONS`). Stub out allauth email adapter (`users/adapter.py`), remove `notify_users()` email logic in `files/methods.py`, remove new-user email alert signal in `users/models.py`. Set `ACCOUNT_EMAIL_VERIFICATION = "none"` so signup works without SMTP. Remove email templates.
- **Depends on:** Remove Contact Feature (contact form sends email — remove that first to reduce scope)
- **Files (~15):**
  - **Backend:** `cms/settings.py` (EMAIL_* settings, INSTALLED_APPS, notification toggles), `users/adapter.py` (stub send_mail), `users/models.py` (post_user_create signal email block), `files/methods.py` (notify_users email logic)
  - **Config:** `requirements.txt` (django-celery-email)
  - **Templates:** `templates/account/email/` (4 email body/subject templates), `templates/account/email.html` (email management page), `templates/account/messages/` (email-related flash messages)

## Done
<!-- Completed items are recorded in docs/changelog.md -->
