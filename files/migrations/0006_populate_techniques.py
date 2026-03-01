import json
import os

from django.db import migrations


def populate_techniques(apps, schema_editor):
    Technique = apps.get_model("files", "Technique")
    TechniqueMedia = apps.get_model("files", "TechniqueMedia")

    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "techniques.json")
    with open(json_path, "r") as f:
        data = json.load(f)

    # Recursively create Technique objects, tracking insertion order for lft/rght
    def create_nodes(nodes, parent=None):
        for node in nodes:
            technique = Technique.objects.create(
                title=node.get("title", ""),
                slug=node.get("id", ""),
                parent=parent,
                status=node.get("status") or "",
                notes=node.get("notes") or "",
                resources=node.get("resources") or [],
                # MPTT fields — will be fixed by rebuild()
                lft=0,
                rght=0,
                tree_id=0,
                level=0,
            )
            children = node.get("children", [])
            if children:
                create_nodes(children, parent=technique)

    create_nodes(data.get("tree", []))

    # Rebuild MPTT tree structure
    Technique.objects.rebuild()

    # Remap TechniqueMedia rows: set the new FK from old technique_id slug
    slug_to_technique = {t.slug: t for t in Technique.objects.all()}
    orphaned_ids = []
    for tm in TechniqueMedia.objects.all():
        technique = slug_to_technique.get(tm.technique_id)
        if technique:
            tm.technique = technique
            tm.save(update_fields=["technique"])
        else:
            orphaned_ids.append(tm.pk)

    # Delete orphaned associations (no matching technique slug)
    if orphaned_ids:
        TechniqueMedia.objects.filter(pk__in=orphaned_ids).delete()


def unpopulate_techniques(apps, schema_editor):
    Technique = apps.get_model("files", "Technique")
    TechniqueMedia = apps.get_model("files", "TechniqueMedia")
    # Clear the FK (we can't restore the old technique_id string)
    TechniqueMedia.objects.update(technique=None)
    Technique.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0005_technique"),
    ]

    operations = [
        migrations.RunPython(populate_techniques, unpopulate_techniques),
    ]
