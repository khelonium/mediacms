from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0009_remove_likes_dislikes"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS files_subtitle CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS files_language CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
