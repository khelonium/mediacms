from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0010_remove_subtitles"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE files_media DROP COLUMN IF EXISTS reported_times;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
