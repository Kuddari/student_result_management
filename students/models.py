# students/models.py

from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100, null=True, blank=True)
    arabic_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField()
    id_number = models.CharField(max_length=13, unique=True)  # Thai ID Card Number

    # Address information
    house_number = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    subdistrict = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)

    # Educational details
    school_name = models.CharField(max_length=100)
    school_english_name = models.CharField(max_length=100, null=True, blank=True)
    current_education_status = models.CharField(max_length=20, choices=[('Studying', 'กำลังศึกษา'), ('Graduated', 'จบการศึกษา')])
    education_district = models.CharField(max_length=100)

    # Special status
    special_status = models.CharField(max_length=20, choices=[('Orphan', 'เด็กกำพร้า'), ('Muallaf', 'มูอัลลิฟ'), ('Poor', 'ยากจน'), ('Disabled', 'พิการ')], blank=True, null=True)

    # Upload image
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Parent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parents")
    parent_type = models.CharField(max_length=10, choices=[('Father', 'บิดา'), ('Mother', 'มารดา')])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    occupation = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100, blank=True, null=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Address Information
    house_number = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    subdistrict = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.parent_type} of {self.student.first_name} {self.student.last_name}"


class Guardian(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="guardian")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    relationship_status = models.CharField(max_length=50, choices=[('Together', 'อยู่ด้วยกัน'), ('Separated', 'แยกกันอยู่'), ('Divorced', 'อย่าร้าง'), ('Other', 'อื่นๆ')])
    occupation = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100, blank=True, null=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Address Information
    house_number = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    subdistrict = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Guardian of {self.student.first_name} {self.student.last_name}"
