import os
import logging

import m3u8
import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from files.models import Media

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download thumbnails, posters, sprites, and HLS manifests from remote MediaCMS server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--remote-host",
            default=None,
            help="Remote host URL (default: settings.REMOTE_MEDIA_HOST)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be downloaded without actually downloading",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Re-download files that already exist locally",
        )

    def handle(self, *args, **options):
        remote_host = options["remote_host"] or getattr(settings, "REMOTE_MEDIA_HOST", None)
        if not remote_host:
            self.stderr.write(self.style.ERROR("REMOTE_MEDIA_HOST not set and --remote-host not provided"))
            return

        remote_host = remote_host.rstrip("/")
        dry_run = options["dry_run"]
        overwrite = options["overwrite"]
        session = requests.Session()

        media_qs = Media.objects.all()
        total = media_qs.count()
        self.stdout.write(f"Processing {total} media objects from {remote_host}")

        stats = {"downloaded": 0, "skipped": 0, "failed": 0}

        for i, media in enumerate(media_qs.iterator(), 1):
            self.stdout.write(f"[{i}/{total}] {media.friendly_token} - {media.title}")

            # Download thumbnail/poster/sprite files
            for field_name in ("thumbnail", "poster", "uploaded_thumbnail", "uploaded_poster", "sprites"):
                field = getattr(media, field_name, None)
                if not field or not field.name:
                    continue
                local_path = os.path.join(settings.MEDIA_ROOT, field.name)
                remote_url = f"{remote_host}{settings.MEDIA_URL}{field.name}"
                self._download_file(session, remote_url, local_path, dry_run, overwrite, stats)

            # Download HLS manifests (not .ts segments)
            if media.hls_file:
                self._sync_hls(session, media.hls_file, remote_host, dry_run, overwrite, stats)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Downloaded: {stats['downloaded']}, Skipped: {stats['skipped']}, Failed: {stats['failed']}"
        ))

    def _download_file(self, session, remote_url, local_path, dry_run, overwrite, stats):
        if os.path.exists(local_path) and not overwrite:
            stats["skipped"] += 1
            return True

        if dry_run:
            self.stdout.write(f"  [DRY-RUN] Would download: {remote_url}")
            stats["downloaded"] += 1
            return True

        try:
            resp = session.get(remote_url, timeout=30, stream=True)
            if resp.status_code != 200:
                self.stderr.write(f"  FAIL ({resp.status_code}): {remote_url}")
                stats["failed"] += 1
                return False

            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.stdout.write(f"  OK: {os.path.basename(local_path)}")
            stats["downloaded"] += 1
            return True
        except requests.RequestException as e:
            self.stderr.write(f"  FAIL: {remote_url} - {e}")
            stats["failed"] += 1
            return False

    def _sync_hls(self, session, hls_file_path, remote_host, dry_run, overwrite, stats):
        """Download master.m3u8 and per-resolution .m3u8 playlists (not .ts segments)."""
        # hls_file_path is absolute, e.g. /home/mediacms.io/mediacms/media_files/hls/{uid}/master.m3u8
        # Convert to relative path under MEDIA_ROOT for URL construction
        if not hls_file_path.startswith(settings.MEDIA_ROOT):
            self.stderr.write(f"  HLS path outside MEDIA_ROOT: {hls_file_path}")
            return

        relative_path = hls_file_path.replace(settings.MEDIA_ROOT, "")
        remote_url = f"{remote_host}{settings.MEDIA_URL}{relative_path}"

        # Download master.m3u8
        if not self._download_file(session, remote_url, hls_file_path, dry_run, overwrite, stats):
            return

        if dry_run:
            return

        # Parse the master playlist to find per-resolution playlists
        if not os.path.exists(hls_file_path):
            return

        try:
            m3u8_obj = m3u8.load(hls_file_path)
        except Exception as e:
            self.stderr.write(f"  Failed to parse HLS manifest: {e}")
            return

        hls_dir = os.path.dirname(hls_file_path)
        hls_dir_relative = os.path.dirname(relative_path)

        # Download each playlist referenced in the master (stream playlists + iframe playlists)
        for playlist in m3u8_obj.playlists:
            playlist_local = os.path.join(hls_dir, playlist.uri)
            playlist_remote = f"{remote_host}{settings.MEDIA_URL}{hls_dir_relative}/{playlist.uri}"
            self._download_file(session, playlist_remote, playlist_local, dry_run, overwrite, stats)

        for iframe_playlist in m3u8_obj.iframe_playlists:
            playlist_local = os.path.join(hls_dir, iframe_playlist.uri)
            playlist_remote = f"{remote_host}{settings.MEDIA_URL}{hls_dir_relative}/{iframe_playlist.uri}"
            self._download_file(session, playlist_remote, playlist_local, dry_run, overwrite, stats)
