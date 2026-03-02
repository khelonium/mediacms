from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0011_remove_reported_times"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE files_media DROP COLUMN IF EXISTS featured;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE files_media DROP COLUMN IF EXISTS user_featured;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
