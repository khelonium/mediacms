from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0006_remove_ratings"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE IF EXISTS files_media DROP COLUMN IF EXISTS license_id;",
                "DROP TABLE IF EXISTS files_license CASCADE;",
            ],
            reverse_sql=[],
        ),
    ]
