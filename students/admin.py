from django.contrib import admin
from django.utils.html import format_html
from .models import *


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'year')
    ordering = ['year']
    search_fields = ['year']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('house_number', 'street', 'subdistrict', 'district', 'province', 'postal_code')
    search_fields = ['province', 'district', 'subdistrict']
    list_filter = ['province', 'district']


@admin.register(CurrentYear)
class CurrentYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'year')
    ordering = ['year']


@admin.register(EducationDistrict)
class EducationDistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ['name']
    ordering = ['name']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name_info','english_name','arabic_name','gender_icon', 'address_info', 'status_icon')
    list_filter = ('status', 'gender')
    search_fields = ('first_name', 'last_name', 'id_number','english_name','arabic_name')

    def name_info(self, obj):
        if obj.first_name:
            return f"{obj.first_name} {obj.last_name}"
        return "ไม่มีข้อมูลที่อยู่"
        

    def name_info(self, obj):
        if obj.first_name:
            return f"{obj.first_name} {obj.last_name}"
        return "ไม่มีข้อมูลที่อยู่"

    name_info.short_description = "ชื่อ - นามสกุล"


    def gender_icon(self, obj):
        """แสดงไอคอนเพศ"""
        if obj.gender == "ชาย":
            return format_html('<i class="fas fa-mars" style="color: blue; font-size: 1.5em;"></i>')
        elif obj.gender == "หญิง":
            return format_html('<i class="fas fa-venus" style="color: red; font-size: 1.5em;"></i>')
        return format_html('<i class="fas fa-genderless" style="color: gray; font-size: 1.5em;"></i>')

    gender_icon.short_description = "เพศ"

    def address_info(self, obj):
        """แสดงข้อมูลที่อยู่"""
        if obj.address:
            return f"{obj.address.house_number} {obj.address.street} ต.{obj.address.subdistrict} อ.{obj.address.district} จ.{obj.address.province}"
        return "ไม่มีข้อมูลที่อยู่"

    address_info.short_description = "ที่อยู่"

    def status_icon(self, obj):
        """แสดงไอคอนสถานะ"""
        if obj.status == 'กำลังศึกษา':
            return format_html('<i class="fas fa-check-circle" style="color: green; font-size: 1.5em;"></i>')
        elif obj.status == 'จบแล้ว':
            return format_html('<i class="fas fa-times-circle" style="color: red; font-size: 1.5em;"></i>')
        return format_html('<i class="fas fa-question-circle" style="color: gray; font-size: 1.5em;"></i>')

    status_icon.short_description = "สถานะ (ไอคอน)"

    def status_icon(self, obj):
        """แสดงไอคอนสถานะ"""
        if obj.status == 'กำลังศึกษา':
            return format_html('<i class="fas fa-check-circle" style="color: green; font-size: 1.5em;"></i>')
        elif obj.status == 'จบแล้ว':
            return format_html('<i class="fas fa-times-circle" style="color: red; font-size: 1.5em;"></i>')
        return format_html('<i class="fas fa-question-circle" style="color: gray; font-size: 1.5em;"></i>')

    status_icon.short_description = "สถานะ"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_marks')
    search_fields = ['name']


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


@admin.register(SubjectToStudy)
class SubjectToStudyAdmin(admin.ModelAdmin):
    list_display = ('subject', 'level', 'semester')
    list_filter = ('semester', 'level')


@admin.register(StudentMarkForSubject)
class StudentMarkForSubjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_to_study', 'marks_obtained')
    search_fields = ['student__first_name', 'student__last_name']
    list_filter = ['subject_to_study__semester', 'subject_to_study__level']


@admin.register(StudentHistory)
class StudentHistoryAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'level_name', 'semester', 'academic_year', 'total_marks', 'obtained_marks','grade_percentage', 'pass_or_fail')
    search_fields = ['student_name']
    list_filter = ['level_name', 'semester']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'education_district')
    search_fields = ['name', 'education_district__name']
    list_filter = ['education_district']

@admin.register(Father)
class FatherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'occupation', 'phone_number')
    search_fields = ['first_name', 'last_name']
    list_filter = ['occupation']

@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'occupation', 'phone_number')
    search_fields = ['first_name', 'last_name']
    list_filter = ['occupation']


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'relationship_with_student', 'phone_number')
    search_fields = ['first_name', 'last_name']
    list_filter = ['relationship_with_student']




@admin.register(CurrentStudy)
class CurrentStudyAdmin(admin.ModelAdmin):
    list_display = ('student', 'level', 'current_semester', 'school')
    search_fields = ['student__first_name', 'student__last_name']
    list_filter = ['level', 'current_semester', 'school']


@admin.register(CurrentSemester)
class CurrentSemesterAdmin(admin.ModelAdmin):
    list_display = ('semester', 'year')
    list_filter = ['semester']
    ordering = ['year']
