from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    USERTYPE = (
        ('aalim', 'aalim'),
        ('admin', 'admin'),
    )
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE
    )
    profile_pic = models.ImageField(
        default="profile1.jpg", null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.CharField(max_length=100, blank=True, choices=USERTYPE)
    date_of_joining = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)


class Maktab(models.Model):
    maktab_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return self.maktab_name


class Syllabus(models.Model):
    subject = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return self.subject


class Alim(models.Model):
    user = models.ForeignKey(
        UserProfile, null=True, blank=True, on_delete=models.CASCADE)
    maktab = models.ManyToManyField(
        Maktab, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self) -> str:
        return self.user.user.get_full_name()


class Student(models.Model):
    maktab = models.ForeignKey(
        Maktab, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    father_name = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    aadhaar_number = models.CharField(max_length=100, null=True, blank=True)
    front_adhaar = models.ImageField(
        default="profile1.jpg", null=True, blank=True)
    back_adhaar = models.ImageField(
        default="profile1.jpg", null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class SyllabusStatus(models.Model):
    student = models.ForeignKey(
        Student, null=True, blank=True, on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Syllabus, null=True, blank=True, on_delete=models.SET_NULL
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self) -> str:
        return self.student.name + ' '+self.subject.subject
