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
    levels_data = [f"ระดับชั้นปี {i}" for i in range(1, 9)]
    
    for level_name in levels_data:
        Level.objects.get_or_create(name=level_name)

    print("Default Levels (ชั้น 1 to ชั้น 8) created.")

# Create default SubjectToStudy for all subjects, all semesters, and all levels
@receiver(post_migrate)
def create_default_subject_to_study(sender, **kwargs):
    subjects = Subject.objects.all()
    levels = Level.objects.all()
    semesters = [1, 2]  # เทอม 1, เทอม 2

    # Loop through all subjects, levels, and semesters and create SubjectToStudy
    for subject in subjects:
        for level in levels:
            for semester in semesters:
                # Check if the record already exists, if not, create it
                SubjectToStudy.objects.get_or_create(
                    subject=subject,
                    level=level,
                    semester=semester
                )

    print("Default SubjectToStudy records created.")