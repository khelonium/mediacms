import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0004_techniquemedia"),
    ]

    operations = [
        # 1. Create the Technique MPTT table
        migrations.CreateModel(
            name="Technique",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.CharField(db_index=True, max_length=200, unique=True)),
                ("status", models.CharField(blank=True, default="", max_length=20)),
                ("notes", models.TextField(blank=True, default="")),
                ("resources", models.JSONField(blank=True, default=list)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="files.technique",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "techniques",
            },
        ),
        # 2. Add temporary nullable FK on TechniqueMedia (alongside old technique_id)
        migrations.AddField(
            model_name="techniquemedia",
            name="technique",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="technique_media",
                to="files.technique",
            ),
        ),
    ]
