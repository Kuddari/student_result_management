# Generated by Django 5.1.2 on 2024-11-25 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0006_alter_studenthistory_academic_year"),
    ]

    operations = [
        migrations.CreateModel(
            name="CurrentSemester",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "semester",
                    models.IntegerField(
                        choices=[(1, "เทอม 1"), (2, "เทอม 2")], default=1
                    ),
                ),
                ("year", models.PositiveIntegerField(default=2024)),
            ],
        ),
    ]