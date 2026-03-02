from django.db import models

from files.models import Media
from users.models import User


class MediaAction(models.Model):
    """Tracks media watch history for users and anonymous sessions."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        blank=True,
        null=True,
        related_name="useractions",
    )
    session_key = models.CharField(
        max_length=33,
        db_index=True,
        blank=True,
        null=True,
        help_text="for not logged in users",
    )

    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name="mediaactions")
    action_date = models.DateTimeField(auto_now_add=True)
    remote_ip = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"watch {self.media}"

    class Meta:
        indexes = [
            models.Index(fields=["user", "-action_date"]),
            models.Index(fields=["session_key"]),
        ]
