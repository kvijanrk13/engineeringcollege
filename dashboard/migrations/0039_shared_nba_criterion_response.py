from django.db import migrations, models


def merge_role_responses(apps, schema_editor):
    Response = apps.get_model("dashboard", "NbaCriterionResponse")
    db_alias = schema_editor.connection.alias
    rows = Response.objects.using(db_alias).all().order_by("tier", "criterion_no", "id")
    grouped = {}
    for row in rows:
        key = (row.tier, row.criterion_no)
        if key not in grouped:
            grouped[key] = row
            continue
        primary = grouped[key]
        if not primary.content and row.content:
            primary.content = row.content
        if not primary.submitted_by and row.submitted_by:
            primary.submitted_by = row.submitted_by
        primary.save(using=db_alias, update_fields=["content", "submitted_by"])
        row.delete(using=db_alias)


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0038_nbacriterionresponse")]

    operations = [
        migrations.RunPython(merge_role_responses, migrations.RunPython.noop),
        migrations.RemoveField(model_name="nbacriterionresponse", name="role"),
        migrations.AlterUniqueTogether(
            name="nbacriterionresponse",
            unique_together={("tier", "criterion_no")},
        ),
    ]
