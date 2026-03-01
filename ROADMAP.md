# Roadmap

## Up Next
<!-- Items in priority order. Move to changelog when done. -->

### Remove Languages / i18n
- **Why:** Functionally dormant — no locale files, no language switcher, no translations exist
- **Scope:** Set `USE_I18N = False`, remove `{% load i18n %}` / `{% trans %}` from allauth templates, remove `gettext_lazy` from validators
- **Files:** `cms/settings.py`, `templates/account/`, `users/validators.py`

### Remove Like Functionality
- **Why:** Simplify the platform — likes/dislikes add complexity without business value for this use case
- **Scope:** Remove Like/Dislike from models, API endpoints, Celery tasks, serializers, React components, navigation, pages, state management, config, templates. Database migration to drop `likes`/`dislikes` columns.
- **Files (~25-30):** `actions/models.py`, `files/models.py`, `files/views.py`, `files/urls.py`, `files/tasks.py`, `files/methods.py`, `files/serializers.py`, `files/management_views.py`, `cms/settings.py`, `frontend/src/.../MediaLikeIcon.jsx`, `frontend/src/.../MediaDislikeIcon.jsx`, `frontend/src/.../ProfileLikedPage.js`, `frontend/src/.../LikedMediaPage.tsx`, `frontend/src/.../MediaPageStore.js`, `frontend/src/.../MediaPageActions.js`, `frontend/src/.../SidebarNavigationMenu.jsx`, `frontend/src/.../member.js`, `frontend/src/.../pages.js`, `frontend/src/.../api.js`, templates

### Remove Email Functionality
- **Why:** Simplify operations — remove SMTP dependency, notification system, contact forms
- **Scope:** Remove email settings, notification system, contact forms, email templates, celery email backend, email verification flow. Replace email-based features with simpler alternatives where needed.
- **Files (~15-20):** `cms/settings.py`, `users/models.py`, `users/adapter.py`, `users/views.py`, `files/methods.py`, `files/views.py`, `files/forms.py`, `templates/account/email/`, `templates/account/email.html`

## Done
<!-- Completed items are recorded in docs/changelog.md -->
