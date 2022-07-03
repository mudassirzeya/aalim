from django.contrib import admin
from .models import UserProfile, Maktab, Syllabus, Alim, Student, SyllabusStatus

admin.site.register(UserProfile)
admin.site.register(Maktab)
admin.site.register(Syllabus)
admin.site.register(Alim)
admin.site.register(Student)
admin.site.register(SyllabusStatus)
