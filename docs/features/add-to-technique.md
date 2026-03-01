# Add Media to Technique

## Overview

Superusers can associate any media item with a node in the technique tree
directly from the media page. This creates a `TechniqueMedia` row in the
database, which the techniques page merges into the JSON tree at read time.

## User flow

1. On any media page, a superuser sees a **TECHNIQUE** button (fitness_center
   icon) in the media actions bar.
2. Clicking it opens a popup with:
   - **Category** dropdown (top-level nodes) with an inline "create new" input.
   - **Subcategory** dropdown (children of the selected category) with "create
     new" input. Shown only when a category is selected.
   - **Technique title** text field (pre-populated or custom).
3. The user selects (or creates) a target node, enters a title, and clicks
   **Add to Technique**.
4. On success a notification appears and the popup closes. If the media is
   already linked to that node, a "duplicate" notification appears (409).

## Frontend components

### `MediaTechniqueButton.jsx`

`frontend/src/static/js/components/media-actions/MediaTechniqueButton.jsx`

Renders the TECHNIQUE button using the `usePopup` hook. The popup content wraps
`TechniqueSelection` via `NavigationContentApp` with a single popup page
(`selectTechnique`).

### `TechniqueSelection.jsx`

`frontend/src/static/js/components/technique-selection/TechniqueSelection.jsx`

Stateful form component. Key state:

| State                  | Purpose                              |
|------------------------|--------------------------------------|
| `tree`                 | Loaded technique tree from API       |
| `selectedCategory`     | Currently selected category ID       |
| `selectedSubcategory`  | Currently selected subcategory ID    |
| `techniqueTitle`       | Title override text                  |
| `newCategoryName`      | Pending new category name            |
| `newSubcategoryName`   | Pending new subcategory name         |

**Submit logic** (`onSubmit`):

- If `newCategoryName` is set with no selected category: creates the category
  (and optionally a subcategory under it) first, then adds the media.
- If a category is selected but `newSubcategoryName` is set: creates the
  subcategory first, then adds the media.
- Otherwise: adds media to the already-selected node.

Category creation calls `POST /api/v1/techniques/categories` directly from the
component, then dispatches `addMediaToTechnique` through the store.

**Validation**: submit is disabled unless both a target node ID and a
non-empty title are provided.

### `TechniqueSelection.scss`

`frontend/src/static/js/components/technique-selection/TechniqueSelection.scss`

- Max-width 320px popup.
- Labels: 12px uppercase with letter-spacing.
- Inputs: full-width, 4px border-radius.
- Create-new section: flex row with input + button.
- Submit button: full-width, theme-colored background.

## State management

### Actions (`MediaPageActions.js`)

| Action                    | Dispatcher type             | Payload                                            |
|---------------------------|-----------------------------|----------------------------------------------------|
| `loadTechniqueTree()`     | `LOAD_TECHNIQUE_TREE`       | —                                                  |
| `addMediaToTechnique()`   | `ADD_MEDIA_TO_TECHNIQUE`    | `technique_id`, `media_friendly_token`, `title_override` |

### Store (`MediaPageStore.js`)

| Dispatcher type           | API call                                  | Success event                          | Failure event                                                    |
|---------------------------|-------------------------------------------|----------------------------------------|------------------------------------------------------------------|
| `LOAD_TECHNIQUE_TREE`     | `GET /api/v1/techniques/tree`             | `technique_tree_loaded`                | `technique_tree_load_failed`                                     |
| `ADD_MEDIA_TO_TECHNIQUE`  | `POST /api/v1/techniques/{id}/media`      | `technique_media_addition_completed`   | `technique_media_already_added` (409) or `technique_media_addition_failed` |

The POST request includes an `X-CSRFToken` header extracted from cookies.

## API endpoints

### Add media to technique

```
POST /api/v1/techniques/{technique_id}/media
```

- **Permission**: `IsSuperUser`
- **Request body**: `{"media_friendly_token": "abc123", "title_override": ""}`
- **201 Created**: returns serialized `TechniqueMedia`
- **400**: missing `media_friendly_token`
- **404**: media not found
- **409**: media already associated with this technique

### Remove media from technique

```
DELETE /api/v1/techniques/{technique_id}/media/{friendly_token}
```

- **Permission**: `IsSuperUser`
- **204 No Content**: association deleted
- **404**: association not found

### Create category

```
POST /api/v1/techniques/categories
```

- **Permission**: `IsSuperUser`
- **Request body**: `{"title": "New Category", "parent_id": "root.guard"}` (`parent_id` optional)
- **201 Created**: `{"id": "root.guard.new-category", "title": "New Category"}`
- **400**: missing `title`
- **404**: `parent_id` not found in tree

The new ID is generated as `(parent_id + "." if parent_id else "root.") + slugify(title)`.
The JSON file is written atomically via temp file + `os.rename()`.

## Model

`TechniqueMedia` (`files/models.py:1579`)

| Field            | Type                          | Notes                                    |
|------------------|-------------------------------|------------------------------------------|
| `technique_id`   | CharField(200), db_index      | Dot-notation node ID                     |
| `media`          | ForeignKey(Media), CASCADE    | `related_name="technique_associations"`  |
| `added_by`       | ForeignKey(User), CASCADE     | Who created the link                     |
| `title_override` | CharField(200), blank         | Optional custom title                    |
| `add_date`       | DateTimeField, auto_now_add   | Timestamp                                |

**Constraints**: `unique_together = ("technique_id", "media")`
**Ordering**: `["-add_date"]` (most recent first)

## Serializer

`TechniqueMediaSerializer` (`files/serializers.py:221`)

| Field            | Source / logic                                  |
|------------------|-------------------------------------------------|
| `friendly_token` | `media.friendly_token` (SerializerMethodField)  |
| `title`          | `title_override or media.title`                 |
| `thumbnail_url`  | `media.thumbnail_url` (read-only)               |
| `url`            | `media.get_absolute_url()`                      |
| `added_by`       | `added_by.username` (read-only)                 |
| `technique_id`   | model field                                     |
| `title_override` | model field                                     |
| `add_date`       | model field (read-only)                         |

## Permissions

- All write endpoints (`TechniqueMediaAdd`, `TechniqueMediaRemove`,
  `TechniqueCategoryCreate`, `TechniqueTreeView`) use the `IsSuperUser`
  permission class (`cms/permissions.py:7`), which checks
  `request.user and request.user.is_superuser`.
- The read endpoint (`TechniquesList`) uses the softer `_is_techniques_user`
  check (superuser or username `"madalina130"`).

## Admin

`TechniqueMediaAdmin` (`files/admin.py:91`)

| Setting          | Value                                      |
|------------------|--------------------------------------------|
| `list_display`   | `technique_id`, `media`, `added_by`, `add_date` |
| `list_filter`    | `technique_id`                             |
| `search_fields`  | `technique_id`, `media__title`             |
| `readonly_fields`| `added_by`, `media`                        |

## Tests

`tests/api/test_technique_media.py` — 13 test cases covering:

| Area           | Tests                                                                 |
|----------------|-----------------------------------------------------------------------|
| Authentication | Anonymous POST redirects/403; regular user POST returns 403           |
| Add media      | Superuser POST returns 201; missing token returns 400; bad token 404  |
| Duplicates     | Second POST for same pair returns 409; DB-level IntegrityError raised |
| Remove media   | Superuser DELETE returns 204; missing association 404; non-super 403  |
| Tree merge     | GET `/api/v1/techniques` includes media merged into the correct node  |
| Tree endpoint  | Regular user GET `/api/v1/techniques/tree` returns 403; super gets 200|

## Key files

| File | Purpose |
|------|---------|
| `files/models.py` | `TechniqueMedia` model |
| `files/views.py` | `TechniqueMediaAdd`, `TechniqueMediaRemove`, `TechniqueCategoryCreate` |
| `files/serializers.py` | `TechniqueMediaSerializer` |
| `files/urls.py` | URL routing |
| `files/admin.py` | `TechniqueMediaAdmin` |
| `cms/permissions.py` | `IsSuperUser` |
| `frontend/.../media-actions/MediaTechniqueButton.jsx` | Trigger button + popup |
| `frontend/.../technique-selection/TechniqueSelection.jsx` | Selection form |
| `frontend/.../technique-selection/TechniqueSelection.scss` | Form styles |
| `frontend/.../utils/actions/MediaPageActions.js` | Flux actions |
| `frontend/.../utils/stores/MediaPageStore.js` | Store event handling |
| `tests/api/test_technique_media.py` | API test coverage |
