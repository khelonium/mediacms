# Techniques Page

## Overview

The `/techniques` page renders a hierarchical tree of BJJ techniques with
associated media (videos) merged in from the database. It is restricted to
authenticated users who pass the `_is_techniques_user` check (superusers or the
hardcoded username `madalina130`).

## Data source

Technique hierarchy lives in `files/data/techniques.json`.

```jsonc
{
  "version": 3,
  "generated_from": ["Bjj.xlsx:Done", "..."],
  "tree": [
    {
      "id": "root.guard",
      "title": "Guard",
      "children": [
        {
          "id": "root.guard.slx",
          "title": "SLX",
          "children": [
            {
              "id": "root.guard.slx.slx-control",
              "title": "Slx Control",
              "status": "done",
              "notes": "Side",
              "resources": [],
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### Node fields

| Field       | Type          | Description                                         |
|-------------|---------------|-----------------------------------------------------|
| `id`        | string        | Dot-notation hierarchical ID (e.g. `root.guard.slx`)|
| `title`     | string        | Human-readable name                                  |
| `status`    | string (opt)  | `"done"` or other status                             |
| `notes`     | string (opt)  | Free-text context                                    |
| `resources` | array         | External links (`{url, source, seed_title}`)         |
| `children`  | array         | Nested child nodes                                   |
| `media`     | array (added) | Injected at runtime by the API merge step            |

## Backend

### Access check

`_is_techniques_user(user)` (`files/views.py:1403`) returns `True` when the
user is authenticated AND either `is_superuser` or username `"madalina130"`.

### HTML view

`techniques()` (`files/views.py:1408`) is a `@login_required` function view.
It checks `_is_techniques_user`, redirects to `/` on failure, otherwise renders
`cms/techniques.html` which mounts the React app at `#page-techniques`.

### API — full tree with media

**`TechniquesList`** (`files/views.py:1414`) handles `GET /api/v1/techniques`.

1. Checks `_is_techniques_user` (returns 403 if denied).
2. Loads `files/data/techniques.json`.
3. Queries all `TechniqueMedia` rows with `.select_related("media", "added_by")`.
4. Builds a `media_by_technique` dict mapping `technique_id` to a list of
   media entry dicts:
   ```python
   {
       "friendly_token": assoc.media.friendly_token,
       "title": assoc.title_override or assoc.media.title,
       "thumbnail_url": assoc.media.thumbnail_url,
       "url": assoc.media.get_absolute_url(),
   }
   ```
5. **Deduplication** — for each technique ID, collects all descendant IDs
   (those starting with `technique_id + "."`), gathers their media tokens, and
   removes those tokens from the parent. This means **the most specific (child)
   node wins**; the same video won't appear at both parent and child level.
6. Calls `_merge_media(tree, media_by_technique)` which recursively injects the
   `media` list into each matching node.
7. Returns the merged tree as JSON.

### API — lightweight tree for dropdowns

**`TechniqueTreeView`** (`files/views.py:1465`) handles
`GET /api/v1/techniques/tree`.

- Permission: `IsSuperUser`.
- Extracts `{id, title, children}` up to depth 2 (categories and
  subcategories only). Used by the technique-selection popup.

## API endpoints

| Method | Path                          | View                | Permission           | Purpose                    |
|--------|-------------------------------|---------------------|----------------------|----------------------------|
| GET    | `/api/v1/techniques`          | `TechniquesList`    | `_is_techniques_user`| Full tree with merged media|
| GET    | `/api/v1/techniques/tree`     | `TechniqueTreeView` | `IsSuperUser`        | Lightweight tree for forms |

## Frontend

### Entry point

`TechniquesPage.tsx` (`frontend/src/static/js/pages/TechniquesPage.tsx`)
fetches `/api/v1/techniques` with credentials, handles loading/error/403
states, counts techniques (nodes with a `status` field), and renders the tree
recursively.

### TypeScript interfaces

- `TechniqueMediaItem` — `{friendly_token, title, thumbnail_url, url}`
- `TechniqueNode` — `{id, title, status?, notes?, resources?, media?, children?}`
- `TechniquesData` — `{version, tree}`

### Recursive rendering (`TechniqueItem`)

| Depth | Element | CSS class                      | Heading |
|-------|---------|--------------------------------|---------|
| 0     | section | `.techniques-category`         | h2      |
| 1     | section | `.techniques-subcategory`      | h3      |
| 2+    | section | `.techniques-sub-subcategory`  | h4      |
| leaf  | li      | `.techniques-item`             | span    |

- `MediaItems` maps media entries to `<li>` elements with `[Watch]` links.
- Notes render as `.techniques-notes` (italic, muted).
- Resources render as `.techniques-link` inline links.

### Styling

`TechniquesPage.scss` (`frontend/src/static/js/pages/TechniquesPage.scss`):

- `.techniques-page` — max-width 900px, 24px padding.
- Category titles get a 2px bottom border.
- Items use a `::before` bullet (`\2022`).
- See also `docs/techniques-styling-guide.md` for the full class reference.

## Key files

| File | Purpose |
|------|---------|
| `files/data/techniques.json` | Technique hierarchy (source of truth) |
| `files/views.py` | `TechniquesList`, `TechniqueTreeView`, `_is_techniques_user` |
| `files/urls.py` | URL routing for technique endpoints |
| `cms/permissions.py` | `IsSuperUser` permission class |
| `templates/cms/techniques.html` | Django template mounting React app |
| `frontend/src/static/js/pages/TechniquesPage.tsx` | React page component |
| `frontend/src/static/js/pages/TechniquesPage.scss` | Page styles |
| `docs/techniques-styling-guide.md` | Detailed styling reference |
