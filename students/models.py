from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # ใช้สำหรับการแปลภาษา
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver


logger = logging.getLogger(__name__)

class Occupation(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("อาชีพ"))

    class Meta:
        verbose_name = _("อาชีพ")
        verbose_name_plural = _("อาชีพ")

class Workplace(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("สถานที่ทำงาน"))

    class Meta:
        verbose_name = _("สถานที่ทำงาน")
        verbose_name_plural = _("สถานที่ทำงาน")

class AcademicYear(models.Model):
    year = models.IntegerField(unique=True, verbose_name=_("ปีการศึกษา"))

    class Meta:
        verbose_name = _("ปีการศึกษา")
        verbose_name_plural = _("ปีการศึกษา")


class Student(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_("ชื่อ"))
    last_name = models.CharField(max_length=100, verbose_name=_("นามสกุล"))
    english_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("ชื่อภาษาอังกฤษ"))
    arabic_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("ชื่อภาษาอาหรับ"))
    date_of_birth = models.DateField(verbose_name=_("วันเกิด"))
    id_number = models.CharField(max_length=13, unique=True, verbose_name=_("เลขบัตรประชาชน"))

    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, verbose_name=_("ที่อยู่"))
    gender = models.CharField(
        max_length=10,
        choices=[('ชาย', 'ชาย'), ('หญิง', 'หญิง')],
        blank=True,
        null=True,
        verbose_name=_("เพศ")
    )
    special_status = models.CharField(
        max_length=20,
        choices=[
            ('เด็กกำพร้า', 'เด็กกำพร้า'),
            ('เด็กยากไร้', 'เด็กยากไร้'),
            ('เด็กพิการ', 'เด็กพิการ'),
            ('เด็กมุอัลลัฟ', 'เด็กมุอัลลัฟ'),
        ],
        blank=True,
        null=True,
        verbose_name=_("สถานะพิเศษ")
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name=_("รูปโปรไฟล์"))
    status = models.CharField(
        max_length=10,
        choices=[('กำลังศึกษา', 'กำลังศึกษา'), ('จบแล้ว', 'จบแล้ว')],
        default='กำลังศึกษา',
        verbose_name=_("สถานะ")
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("นักเรียน")
        verbose_name_plural = _("นักเรียน")


class CurrentSemester(models.Model):
    semester = models.IntegerField(
        choices=[(1, 'เทอม 1'), (2, 'เทอม 2')],
        default=1,
        verbose_name=_("ภาคการศึกษา")
    )
    year = models.PositiveIntegerField(default=timezone.now().year, verbose_name=_("ปีการศึกษา"))
    
    def save(self, *args, **kwargs):
        from .models import StudentMarkForSubject  # Import inside the method to avoid circular imports

        # Enforce singleton constraint
        if not self.pk and CurrentSemester.objects.exists():
            raise ValueError("มีข้อมูลภาคการศึกษาได้เพียงหนึ่งรายการ")

        # Check for updates on existing instance
        if self.pk:
            old_instance = CurrentSemester.objects.get(pk=self.pk)
            logger.info(f"Old Semester: {old_instance.semester}, New Semester: {self.semester}")
            logger.info(f"Old Year: {old_instance.year}, New Year: {self.year}")

            if old_instance.semester != self.semester or old_instance.year != self.year:
                logger.info("Semester or Year has changed. Deleting all StudentMarkForSubject records.")
                StudentMarkForSubject.objects.all().delete()

        # Call the original save method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_semester_display()} - {self.year}"

    class Meta:
        verbose_name = _("ภาคการศึกษา")
        verbose_name_plural = _("ภาคการศึกษา")


class CurrentStudy(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='current_study', verbose_name=_("นักเรียน"))
    level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True, verbose_name=_("ระดับชั้น"))
    current_semester = models.ForeignKey(CurrentSemester, on_delete=models.SET_NULL, null=True, verbose_name=_("ภาคการศึกษา"))
    school = models.ForeignKey('School', on_delete=models.SET_NULL, null=True, verbose_name=_("โรงเรียน"))

    def save(self, *args, **kwargs):
        # Automatically assign the latest CurrentSemester if not already set
        if not self.current_semester_id:
            self.current_semester = CurrentSemester.objects.first()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.level.name}, Semester {self.current_semester.semester}, Year {self.current_semester.year}"

    class Meta:
        verbose_name = _("การศึกษาในปัจจุบัน")
        verbose_name_plural = _("การศึกษาในปัจจุบัน")

# Signal to update CurrentStudy when CurrentSemester changes
@receiver(post_save, sender=CurrentSemester)
def update_current_study(sender, instance, **kwargs):
    CurrentStudy.objects.update(current_semester=instance)

class Level(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("ชื่อระดับชั้น"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("ระดับชั้น")
        verbose_name_plural = _("ระดับชั้น")

class School(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("ชื่อโรงเรียน"))
    english_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("ชื่อโรงเรียน (ภาษาอังกฤษ)"))
    education_district = models.ForeignKey('EducationDistrict', on_delete=models.CASCADE, related_name='schools', verbose_name=_("เขตการศึกษา"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("โรงเรียน")
        verbose_name_plural = _("โรงเรียน")


class EducationDistrict(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("ชื่อเขตการศึกษา"))
    description = models.TextField(blank=True, null=True, verbose_name=_("คำอธิบาย"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("เขตการศึกษา")
        verbose_name_plural = _("เขตการศึกษา")


class ParentBase(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="%(class)s_set", verbose_name=_("นักเรียน"))
    first_name = models.CharField(max_length=100, verbose_name=_("ชื่อ"))
    last_name = models.CharField(max_length=100, verbose_name=_("นามสกุล"))
    date_of_birth = models.DateField(verbose_name=_("วันเกิด"))
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, verbose_name=_("ที่อยู่"))
    occupation = models.ForeignKey('Occupation', on_delete=models.SET_NULL, null=True, verbose_name=_("อาชีพ"))
    workplace = models.ForeignKey('Workplace', on_delete=models.SET_NULL, null=True, verbose_name=_("สถานที่ทำงาน"))
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("รายได้"))
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("หมายเลขโทรศัพท์"))

    class Meta:
        abstract = True


class Father(ParentBase):
    def __str__(self):
        return f"Father: {self.first_name} {self.last_name} - {self.student}"

    class Meta:
        verbose_name = _("บิดา")
        verbose_name_plural = _("บิดา")


class Mother(ParentBase):
    def __str__(self):
        return f"Mother: {self.first_name} {self.last_name} - {self.student}"

    class Meta:
        verbose_name = _("มารดา")
        verbose_name_plural = _("มารดา")


class Guardian(ParentBase):
    relationship_with_student = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("ความสัมพันธ์กับนักเรียน"))

    def __str__(self):
        return f"Guardian: {self.first_name} {self.last_name} - {self.student}"

    class Meta:
        verbose_name = _("ผู้ปกครอง")
        verbose_name_plural = _("ผู้ปกครอง")


class Address(models.Model):
    house_number = models.CharField(max_length=10, verbose_name=_("บ้านเลขที่"))
    street = models.CharField(max_length=100, verbose_name=_("ถนน"))
    subdistrict = models.CharField(max_length=50, verbose_name=_("ตำบล/แขวง"))
    district = models.CharField(max_length=50, verbose_name=_("อำเภอ/เขต"))
    province = models.CharField(max_length=50, verbose_name=_("จังหวัด"))
    postal_code = models.CharField(max_length=5, verbose_name=_("รหัสไปรษณีย์"))
    contact_number = models.CharField(max_length=15, verbose_name=_("เบอร์โทรติดต่อ"))

    def __str__(self):
        return f"{self.house_number}, {self.street}, {self.subdistrict}, {self.district}, {self.province}, {self.postal_code}"

    class Meta:
        verbose_name = _("ที่อยู่")
        verbose_name_plural = _("ที่อยู่")


class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("ชื่อวิชา"))
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("คะแนนเต็ม"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("วิชา")
        verbose_name_plural = _("วิชา")


class SubjectToStudy(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_("วิชา"))
    level = models.ForeignKey('Level', on_delete=models.CASCADE, verbose_name=_("ระดับชั้น"))
    semester = models.IntegerField(
        choices=[(1, 'เทอม 1'), (2, 'เทอม 2')],
        default=1,
        verbose_name=_("ภาคการศึกษา")
    )

    class Meta:
        verbose_name = _("วิชาที่เรียน")
        verbose_name_plural = _("วิชาที่เรียน")


class StudentMarkForSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_("นักเรียน"))
    subject_to_study = models.ForeignKey(SubjectToStudy, on_delete=models.CASCADE, verbose_name=_("วิชาที่เรียน"))
    marks_obtained = models.IntegerField(blank=True, null=True, default=0, verbose_name=_("คะแนนที่ได้"))
    class Meta:
        verbose_name = _("คะแนนนักเรียนสำหรับวิชา")
        verbose_name_plural = _("คะแนนนักเรียนสำหรับวิชา")

class StudentHistory(models.Model):
    student_name = models.CharField(blank=True, null=True,max_length=255, verbose_name=_("ชื่อนักเรียน"))
    school_name = models.CharField(blank=True, null=True,max_length=255, verbose_name=_("ชื่อโรงเรียน"))
    level_name = models.CharField(blank=True, null=True,max_length=50, verbose_name=_("ระดับชั้น"))
    semester = models.CharField(blank=True, null=True,max_length=50, verbose_name=_("ภาคการศึกษา"))
    academic_year = models.CharField(blank=True, null=True,max_length=4, verbose_name=_("ปีการศึกษา"))
    total_marks = models.IntegerField(blank=True, null=True, default=0, verbose_name=_("คะแนนเต็ม"))
    obtained_marks = models.IntegerField(blank=True, null=True, default=0, verbose_name=_("คะแนนที่ได้"))
    grade_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_("เปอร์เซ็นต์คะแนน"))
    subject_marks = models.JSONField(blank=True, null=True, verbose_name=_("คะแนนตามวิชา"))
    #grade_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_("เปอร์เซ็นต์คะแนน"))
    pass_or_fail = models.CharField(max_length=4, blank=True, null=True, verbose_name=_("ผ่าน/ไม่ผ่าน"))
    def calculate_grades(self):
        """Calculate grades based on subject marks and compute grade percentage."""
        if self.subject_marks:

            # Calculate total and obtained marks
            self.total_marks = sum(self.subject_marks.values())
            self.obtained_marks = sum(self.subject_marks.values())

            # Calculate grade percentage
            if self.total_marks > 0:
                self.grade_percentage = (self.obtained_marks / self.total_marks) * 100
            else:
                self.grade_percentage = 0

                # Determine pass or fail
                self.pass_or_fail = "ผ่าน" if self.grade_percentage >= 50 else "ไม่ผ่าน"

                self.save()

    def __str__(self):
        return f"{self.student_name} - {self.level_name} - {self.academic_year}"

    class Meta:
        verbose_name = _("ประวัติการศึกษา")
        verbose_name_plural = _("ประวัติการศึกษา")

 