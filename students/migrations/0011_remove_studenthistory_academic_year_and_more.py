# Generated by Django 5.1.2 on 2024-11-25 16:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0010_alter_currentstudy_current_semester"),
    ]

    operations = [
        migrations.RemoveField(model_name="studenthistory", name="academic_year",),
        migrations.AlterField(
            model_name="studenthistory",
            name="semester",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="students.currentsemester",
            ),
        ),
        migrations.CreateModel(
            name="StudentHistorys",
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
                    "academic_year",
                    models.CharField(blank=True, max_length=4, null=True),
                ),
                (
                    "total_marks",
                    models.DecimalField(decimal_places=2, default=0, max_digits=6),
                ),
                (
                    "obtained_marks",
                    models.DecimalField(decimal_places=2, default=0, max_digits=6),
                ),
                (
                    "grade_percentage",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=5, null=True
                    ),
                ),
                ("pass_or_fail", models.CharField(blank=True, max_length=4, null=True)),
                ("subject_marks", models.JSONField(blank=True, null=True)),
                (
                    "level",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="students.level"
                    ),
                ),
                (
                    "semester",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="students.semester",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="students.student",
                    ),
                ),
            ],
        ),
    ]
