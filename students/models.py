# students/models.py

from django.db import models


class CurrentYear(models.Model):
    year = models.IntegerField(unique=True)

class Occupation(models.Model):
    name = models.CharField(max_length=100)

class Workplace(models.Model):
    name = models.CharField(max_length=100)

class AcademicYear(models.Model):
    year = models.IntegerField(unique=True)


## Student Model
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100, null=True, blank=True)
    arabic_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField()
    id_number = models.CharField(max_length=13, unique=True)  # Thai ID Card Number
    
    # Address information
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True)
    
    # Special status
    special_status = models.CharField(max_length=20, 
     blank=True, null=True)

    # Upload image
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


## Educational Details 
class CurrentStudy(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='current_study')
    level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey('Semester', on_delete=models.SET_NULL, null=True)
    current_year = models.ForeignKey('CurrentYear', on_delete=models.SET_NULL, blank=True, null=True)
    school = models.ForeignKey('School', on_delete=models.SET_NULL, null=True)  # Add this line

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.level.name}, {self.semester.name}, {self.current_year.year}"


## Level Model
class Level(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


## Semester Model
class Semester(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


## School Model
class School(models.Model):
    name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100, null=True, blank=True)
    education_district = models.ForeignKey('EducationDistrict', on_delete=models.CASCADE, related_name='schools')

    def __str__(self):
        return self.name


## Education District Model
class EducationDistrict(models.Model):
    name = models.CharField(max_length=100) 
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


## Parent Base Model
class ParentBase(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="%(class)s_set")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    # Address Information
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True)

    # Linking to the Occupation and Workplace models
    occupation = models.ForeignKey('Occupation', on_delete=models.SET_NULL, null=True)  
    workplace = models.ForeignKey('Workplace', on_delete=models.SET_NULL, null=True)  
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Add income field
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Add phone number field

    class Meta:
        abstract = True


## Relationship Details
class Father(ParentBase):
    def __str__(self):
        return f"Father: {self.first_name} {self.last_name} - {self.student}"


class Mother(ParentBase):
    def __str__(self):
        return f"Mother: {self.first_name} {self.last_name} - {self.student}"


class Guardian(ParentBase):
    relationship_with_student = models.CharField(max_length=50,  blank=True, null=True)

    def __str__(self):
        return f"Guardian: {self.first_name} {self.last_name} - {self.student}"


## Address Model
class Address(models.Model):
    house_number = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    subdistrict = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.house_number}, {self.street}, {self.subdistrict}, {self.district}, {self.province}, {self.postal_code}"


## Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=255)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


## Subject to Study Model
class SubjectToStudy(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    level = models.ForeignKey('Level', on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)


## Student Mark for Subject Model
class StudentMarkForSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_to_study = models.ForeignKey(SubjectToStudy, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)


## Student History Model
class StudentHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    level = models.ForeignKey('Level', on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=4, blank=True, null=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grade_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    pass_or_fail = models.CharField(max_length=4, blank=True, null=True)
    subject_marks = models.JSONField(blank=True, null=True)

    def calculate_history(self):
        # Retrieve all marks for the student's subjects in the given semester and level
        subject_marks = StudentMarkForSubject.objects.filter(
            student=self.student,
            subject_to_study__year_level=self.year_level,
            subject_to_study__semester=self.semester
        )
        
        # Calculate total and obtained marks
        self.total_marks = sum([subject.subject_to_study.subject.total_marks for subject in subject_marks])
        self.obtained_marks = sum([subject.marks_obtained for subject in subject_marks])
        
        # Store marks per subject in the JSON field
        self.subject_marks = {subject.subject_to_study.subject.name: subject.marks_obtained for subject in subject_marks}
        
        # Calculate grade percentage
        if self.total_marks > 0:
            self.grade_percentage = (self.obtained_marks / self.total_marks) * 100
        
        # Determine pass or fail
        self.pass_or_fail = "Pass" if self.grade_percentage >= 50 else "Fail"
        
        # Save updated fields
        self.save()
