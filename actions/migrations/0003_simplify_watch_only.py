from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("actions", "0003_auto_20201201_0712"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE actions_mediaaction DROP COLUMN IF EXISTS extra_info;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE actions_mediaaction DROP COLUMN IF EXISTS action;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
