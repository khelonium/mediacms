import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("files", "0003_auto_20210927_1245"),
    ]

    operations = [
        migrations.CreateModel(
            name="TechniqueMedia",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("technique_id", models.CharField(db_index=True, max_length=200)),
                ("title_override", models.CharField(blank=True, max_length=200)),
                ("add_date", models.DateTimeField(auto_now_add=True)),
                ("added_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("media", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="technique_associations", to="files.media")),
            ],
            options={
                "ordering": ["-add_date"],
                "unique_together": {("technique_id", "media")},
            },
        ),
    ]
