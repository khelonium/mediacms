from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0012_remove_featured"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS files_techniquemedia CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS files_technique CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
