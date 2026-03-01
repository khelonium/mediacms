from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0007_finalize_technique_fk"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Comment",
        ),
        migrations.RemoveField(
            model_name="media",
            name="enable_comments",
        ),
    ]
