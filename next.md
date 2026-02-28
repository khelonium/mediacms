# Next Steps

## Active Now

- Verify full stack works end-to-end: `make up` → upload a video → confirm transcoding completes
- Review `cms/settings.py` for local dev customizations (PORTAL_WORKFLOW, CAN_ADD_MEDIA, etc.)

## Queued

1. Explore frontend dev workflow (`frontend/` React app, `npm run start`)
2. Set up local user accounts and test role-based access (advancedUser, editor, manager)
3. Investigate media processing pipeline (FFmpeg profiles, HLS generation)
4. Review REST API endpoints and test with Swagger UI
