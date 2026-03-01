import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0006_populate_techniques"),
    ]

    operations = [
        # 1. Remove old technique_id CharField
        migrations.RemoveField(
            model_name="techniquemedia",
            name="technique_id",
        ),
        # 2. Make technique FK non-nullable
        migrations.AlterField(
            model_name="techniquemedia",
            name="technique",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="technique_media",
                to="files.technique",
            ),
        ),
        # 3. Update unique_together to use the FK
        migrations.AlterUniqueTogether(
            name="techniquemedia",
            unique_together={("technique", "media")},
        ),
    ]
