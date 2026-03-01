import json
import os

from django.db import migrations


def populate_techniques(apps, schema_editor):
    Technique = apps.get_model("files", "Technique")
    TechniqueMedia = apps.get_model("files", "TechniqueMedia")

    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "techniques.json")
    with open(json_path, "r") as f:
        data = json.load(f)

    tree_id_seq = [0]

    def create_nodes(nodes, parent=None, level=0, counter=None):
        for node in nodes:
            if parent is None:
                tree_id_seq[0] += 1
                counter = [1]

            lft = counter[0]
            counter[0] += 1

            children_data = node.get("children", [])

            technique = Technique.objects.create(
                title=node.get("title", ""),
                slug=node.get("id", ""),
                parent=parent,
                status=node.get("status") or "",
                notes=node.get("notes") or "",
                resources=node.get("resources") or [],
                lft=lft,
                rght=0,
                tree_id=tree_id_seq[0],
                level=level,
            )

            if children_data:
                create_nodes(children_data, parent=technique, level=level + 1, counter=counter)

            technique.rght = counter[0]
            counter[0] += 1
            technique.save(update_fields=["rght"])

    create_nodes(data.get("tree", []))

    # Remap TechniqueMedia rows: set the new FK from old technique_id slug
    slug_to_technique = {t.slug: t for t in Technique.objects.all()}
    orphaned_ids = []
    for tm in TechniqueMedia.objects.all():
        technique = slug_to_technique.get(tm.technique_id)
        if technique:
            tm.technique_fk = technique
            tm.save(update_fields=["technique_fk"])
        else:
            orphaned_ids.append(tm.pk)

    # Delete orphaned associations (no matching technique slug)
    if orphaned_ids:
        TechniqueMedia.objects.filter(pk__in=orphaned_ids).delete()


def unpopulate_techniques(apps, schema_editor):
    Technique = apps.get_model("files", "Technique")
    TechniqueMedia = apps.get_model("files", "TechniqueMedia")
    # Restore technique_id from the FK before clearing
    # (0007 reverse has already re-added the technique_id column and renamed FK back)
    for tm in TechniqueMedia.objects.select_related("technique_fk").all():
        if tm.technique_fk:
            tm.technique_id = tm.technique_fk.slug
            tm.save(update_fields=["technique_id"])
    TechniqueMedia.objects.update(technique_fk=None)
    Technique.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0005_technique"),
    ]

    operations = [
        migrations.RunPython(populate_techniques, unpopulate_techniques),
    ]
