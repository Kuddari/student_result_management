from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django import forms

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Amphoe)
class AmphoeAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']
    list_filter = ['province']

@admin.register(Tambon)
class TambonAdmin(admin.ModelAdmin):
    list_display = ['name', 'amphoe', 'zipcode']
    list_filter = ['amphoe']

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'year')
    ordering = ['year']
    search_fields = ['year']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['house_number', 'street', 'moo', 'province', 'district', 'subdistrict', 'zipcode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter district choices based on the selected province (by ID)
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['district'].queryset = Amphoe.objects.filter(province_id=province_id)
            except (ValueError, TypeError):
                self.fields['district'].queryset = Amphoe.objects.none()
        elif self.instance.pk and self.instance.province:
            self.fields['district'].queryset = self.instance.province.amphoes.all()
        else:
            self.fields['district'].queryset = Amphoe.objects.none()

        # Filter subdistrict choices based on the selected district (by ID)
        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['subdistrict'].queryset = Tambon.objects.filter(amphoe_id=district_id)
            except (ValueError, TypeError):
                self.fields['subdistrict'].queryset = Tambon.objects.none()
        elif self.instance.pk and self.instance.district:
            self.fields['subdistrict'].queryset = self.instance.district.tambons.all()
        else:
            self.fields['subdistrict'].queryset = Tambon.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        subdistrict = cleaned_data.get('subdistrict')
        
        # Automatically set the zipcode based on the selected subdistrict
        if subdistrict:
            cleaned_data['zipcode'] = subdistrict.zipcode

        return cleaned_data
    
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    #form = AddressForm
    list_display = ['house_number', 'province', 'district', 'subdistrict', 'zipcode']
    list_filter = ['province', 'district', 'subdistrict']
    search_fields = ['house_number', 'street', 'moo', 'zipcode']
    fields = ['house_number', 'street', 'moo', 'province', 'district', 'subdistrict', 'zipcode']

    def save_model(self, request, obj, form, change):
        # Automatically set zipcode based on the selected subdistrict
        if obj.subdistrict:
            obj.zipcode = obj.subdistrict.zipcode
        super().save_model(request, obj, form, change)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_info', 'gender_icon', 'subject', 'status_icon', 'password')
    list_filter = ('status', 'gender')
    search_fields = ('first_name', 'last_name', 'id_number', 'subject')

    fields = [
        'gender',
        'first_name',
        'last_name',
        'date_of_birth',
        'id_number',
        'subject',
        'profile_picture',
        'status',
        'password',  # Password as a read-only field
    ]

    readonly_fields = ('password',)  # Prevent editing password manually

    def name_info(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    name_info.short_description = "ชื่อ-นามสกุล"

    def gender_icon(self, obj):
        return "👨‍🏫" if obj.gender == 'ชาย' else "👩‍🏫"
    gender_icon.short_description = "เพศ"

    def status_icon(self, obj):
        return "✅" if obj.status == 'กำลังสอน' else "⚠️"
    status_icon.short_description = "สถานะ"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_info','english_first_name','arabic_first_name','gender_icon', 'address_info', 'status_icon')
    list_filter = ('status', 'gender')
    search_fields = ('first_name', 'last_name', 'id_number','english_first_name','arabic_first_name')
    # Order of fields in the admin form
    fields = [
        'gender',          # Gender first
        'first_name',
        'last_name',
        'english_first_name',
        'arabic_first_name',
        'date_of_birth',
        'id_number',
        'address',
        'special_status',
        'profile_picture',
        'status',
    ]
    

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

@admin.register(SubjectToStudy)
class SubjectToStudyAdmin(admin.ModelAdmin):
    list_display = ('subject', 'level', 'semester')
    list_filter = ('semester', 'level')

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
    # Fields to display in the list view
    list_display = ('student', 'level', 'current_semester', 'school')
    
    # Fields to search by
    search_fields = ['student__first_name', 'student__last_name']
    
    # Filters for the sidebar
    list_filter = ['level', 'current_semester', 'school']
    
    # Exclude 'current_semester' from the form
    exclude = ('current_semester',)

    def get_readonly_fields(self, request, obj=None):
        # Optionally make 'current_semester' readonly instead of excluding it
        return ('current_semester',) if obj else ()
    


@admin.register(CurrentSemester)
class CurrentSemesterAdmin(admin.ModelAdmin):
    # Exclude the 'year' field from the form
    exclude = ('year',)

    # Display fields in the admin list view
    list_display = ('semester', 'year')
    
    # Ordering of records in the list view
    ordering = ['year']

    def save_model(self, request, obj, form, change):
        # Automatically set the year to the current year before saving
        if not obj.year:
            obj.year = timezone.now().year
        super().save_model(request, obj, form, change)

    # Make the model read-only by removing all action buttons
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True  # Allow viewing the model
