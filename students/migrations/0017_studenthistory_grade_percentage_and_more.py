# Generated by Django 5.1.4 on 2024-12-07 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0016_alter_currentsemester_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studenthistory',
            name='grade_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='เปอร์เซ็นต์คะแนน'),
        ),
        migrations.AlterField(
            model_name='studenthistory',
            name='obtained_marks',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='คะแนนที่ได้'),
        ),
        migrations.AlterField(
            model_name='studenthistory',
            name='total_marks',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='คะแนนเต็ม'),
        ),
        migrations.AlterField(
            model_name='studentmarkforsubject',
            name='marks_obtained',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='คะแนนที่ได้'),
        ),
    ]
