from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_remove_notifications"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE users_user DROP COLUMN IF EXISTS allow_contact;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
