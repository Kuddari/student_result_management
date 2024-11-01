# students/forms.py

from django import forms
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    special_status = forms.MultipleChoiceField(
        choices=[
            ('Orphan', 'เด็กกำพร้า'),
            ('Muallaf', 'มูอัลลิฟ'),
            ('Poor', 'ยากจน'),
            ('Disabled', 'พิการ')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select all that apply"
    )

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'english_name', 'arabic_name', 
            'date_of_birth', 'id_number', 'house_number', 'street', 
            'subdistrict', 'district', 'province', 'postal_code', 
            'contact_number', 'school_name', 'school_english_name', 
            'current_education_status', 'education_district', 
             'profile_picture'
        ]
