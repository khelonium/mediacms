# Techniques Page Styling Guide

Visual hierarchy for the `/techniques` tree rendering.

## Component Structure

All rendering is handled by `TechniqueItem` (recursive) and `MediaItems` (fragment helper) in `frontend/src/static/js/pages/TechniquesPage.tsx`.

## Depth Mapping

| Depth | Role | HTML | CSS class | Visual |
|-------|------|------|-----------|--------|
| 0 | Category | `<div>` + `<h2>` | `.techniques-category` | Bold 20px title + green underline |
| 1 | Subcategory | `<div>` + `<h3>` | `.techniques-subcategory` | Bold 16px title, always rendered regardless of children |
| 2 | Sub-subcategory (container) | `<li>` + `<h4>` | `.techniques-sub-subcategory` | Italic 14px title (only if has children AND no status) |
| 2+ | Leaf technique | `<li>` | `.techniques-item` | bullet + black 14px title + optional bracketed resource links |
| any | DB media item | `<li>` (same as leaf) | `.techniques-item` | bullet + black 14px title + `[Watch]` bracketed link |

## Key Rules

- **All items in a single `<ul>`**: Media items and JSON children render in the same list, never separate lists.
- **Media items match regular items**: Black title + bracketed link — never styled as standalone colored links.
- **Depth=1 always subcategory**: A depth-1 node always renders with `<h3>` regardless of whether it has children or media.
- **Bracketed links**: Resource links use `.techniques-link` which adds `[` / `]` via CSS `::before` / `::after` pseudo-elements.

## CSS Classes Reference

| Class | Purpose |
|-------|---------|
| `.techniques-page` | Page container (max-width 900px, centered) |
| `.techniques-category` | Depth-0 wrapper |
| `.techniques-category-title` | `<h2>` with bottom border |
| `.techniques-subcategory` | Depth-1 wrapper |
| `.techniques-subcategory-title` | `<h3>` header |
| `.techniques-sub-subcategory` | Depth-2 container `<li>` (no bullet) |
| `.techniques-sub-subcategory-title` | `<h4>` italic header |
| `.techniques-list` | `<ul>` with left padding, no list-style |
| `.techniques-item` | `<li>` with bullet via `::before` |
| `.techniques-item-title` | `<span>` for technique name |
| `.techniques-notes` | Italic gray notes text |
| `.techniques-resources` | Wrapper for resource links |
| `.techniques-link` | `<a>` with `[brackets]` via pseudo-elements |
