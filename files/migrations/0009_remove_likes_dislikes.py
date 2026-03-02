from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0008_remove_comments"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="media",
            name="likes",
        ),
        migrations.RemoveField(
            model_name="media",
            name="dislikes",
        ),
    ]
