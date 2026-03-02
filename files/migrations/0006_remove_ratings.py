from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0005_technique_techniquemedia"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS files_rating CASCADE;",
                "DROP TABLE IF EXISTS files_ratingcategory CASCADE;",
                "DROP TABLE IF EXISTS files_media_rating_category CASCADE;",
            ],
            reverse_sql=[],
        ),
    ]
