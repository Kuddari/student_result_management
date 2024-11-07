# students/admin.py

from django.contrib import admin
from .models import *
# Register each model with the Django admin site
admin.site.register(AcademicYear)
admin.site.register(Address)
admin.site.register(CurrentYear)
admin.site.register(EducationDistrict)
admin.site.register(Level)
admin.site.register(Occupation)
admin.site.register(Semester)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Workplace)
admin.site.register(SubjectToStudy)
admin.site.register(StudentMarkForSubject)
admin.site.register(StudentHistory)
admin.site.register(School)
admin.site.register(Mother)
admin.site.register(Guardian)
admin.site.register(Father)
admin.site.register(CurrentStudy)

