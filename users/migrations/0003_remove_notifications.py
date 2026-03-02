from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_remove_notification_on_comments"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS users_notification CASCADE;",
                "DROP TABLE IF EXISTS users_channel_subscribers CASCADE;",
            ],
            reverse_sql=[],
        ),
    ]
