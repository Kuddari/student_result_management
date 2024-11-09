# Generated by Django 4.2.16 on 2024-11-04 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0004_alter_guardian_relationship_with_student"),
    ]

    operations = [
        migrations.AlterField(
            model_name="currentstudy",
            name="current_year",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="students.currentyear",
            ),
        ),
    ]