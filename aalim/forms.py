from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['added_date']

        widgets = {
            'maktab': forms.Select(attrs={
                'class': "form-control",
                'required': 'required',
            }),
            'name': forms.TextInput(attrs={
                'class': "form-control",
                'required': "required",
            }),
            'father_name': forms.TextInput(attrs={
                'class': "form-control",
                'required': "required",
            }),
            'student_phone': forms.TextInput(attrs={
                'class': "form-control",
                # 'required': "required",
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': "form-control",
                'required': "required",
            }),
            'address': forms.Textarea(attrs={
                'class': "form-control",
                'required': "required",
            }),
            'aadhaar_number': forms.TextInput(attrs={
                'class': "form-control",
                'required': "required",
            }),
            # 'front_adhaar': forms.ImageField(attrs={
            #     'class': "form-control",
            #     'required': "required",
            # }),
            # 'back_adhaar': forms.ImageField(attrs={
            #     'class': "form-control",
            #     'required': "required",
            # }),

        }
