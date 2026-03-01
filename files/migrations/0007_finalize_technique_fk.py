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
        # 2. Rename technique_fk → technique (also renames column technique_fk_id → technique_id)
        migrations.RenameField(
            model_name="techniquemedia",
            old_name="technique_fk",
            new_name="technique",
        ),
        # 3. Make technique FK non-nullable
        migrations.AlterField(
            model_name="techniquemedia",
            name="technique",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="technique_media",
                to="files.technique",
            ),
        ),
        # 4. Update unique_together to use the FK
        migrations.AlterUniqueTogether(
            name="techniquemedia",
            unique_together={("technique", "media")},
        ),
    ]
