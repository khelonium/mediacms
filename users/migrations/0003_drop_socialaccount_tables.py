from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_remove_notification_on_comments"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""\
DROP TABLE IF EXISTS socialaccount_socialtoken CASCADE;
DROP TABLE IF EXISTS socialaccount_socialapp_sites CASCADE;
DROP TABLE IF EXISTS socialaccount_socialapp CASCADE;
DROP TABLE IF EXISTS socialaccount_socialaccount CASCADE;
DELETE FROM django_migrations WHERE app = 'socialaccount';
""",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
