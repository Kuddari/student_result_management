from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import *
from django.utils import timezone

@receiver(post_migrate)
def create_default_current_semester(sender, **kwargs):
    if not CurrentSemester.objects.exists():
        CurrentSemester.objects.create(semester=1, year=timezone.now().year)
        print("Default CurrentSemester (เทอม 1) created.")

@receiver(post_migrate)
def create_default_subjects(sender, **kwargs):
    subjects_data = [
        {"name": "อัลกะบาอิร", "total_marks": 100.00},
        {"name": "ตัจญ์วีด", "total_marks": 100.00},
        {"name": "ตะเซาวุฟ", "total_marks": 100.00},
        {"name": "ศาสนประวัติ", "total_marks": 100.00},
        {"name": "อัล - หะดิษ", "total_marks": 100.00},
        {"name": "อัลกรุอาน", "total_marks": 100.00},
        {"name": "ฟิกห์", "total_marks": 100.00},
        {"name": "เตาฮีด", "total_marks": 100.00},
    ]

    for subject_data in subjects_data:
        Subject.objects.get_or_create(name=subject_data["name"], defaults={"total_marks": subject_data["total_marks"]})

    print("Default Subjects created.")


@receiver(post_migrate)
def create_default_levels(sender, **kwargs):
    levels_data = [f"ชั้นปี {i}" for i in range(1, 9)]
    
    for level_name in levels_data:
        Level.objects.get_or_create(name=level_name)

    print("Default Levels (ชั้น 1 to ชั้น 8) created.")