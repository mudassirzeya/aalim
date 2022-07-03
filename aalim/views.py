# from this import s
# from time import strptime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Alim, Maktab, Student, Syllabus, SyllabusStatus, UserProfile
from .forms import StudentForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage
import json
# import datetime


# Create your views here.


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("user", password, username)
        user = authenticate(request, username=username, password=password)
        print("us", user)
        if user is not None:
            login(request, user)
            staffProfile = UserProfile.objects.get(user=user)
            usertype = staffProfile.user_type
            if usertype == 'admin':
                return redirect('admin_page')
            elif usertype == 'aalim':
                return redirect('/')
        else:
            messages.info(request, 'Username or Password is in correct')
    context = {}
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    return redirect('user_login')


@login_required(login_url='user_login')
def admin_home(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    if usertype == 'aalim':
        return redirect('/')
    all_maktab = Maktab.objects.all()
    total_maktab = all_maktab.count()
    all_aalim = UserProfile.objects.filter(user_type='aalim')
    total_aalim = all_aalim.count()
    all_student = Student.objects.all()
    total_student = all_student.count()
    context = {'total_maktab': total_maktab,
               'total_aalim': total_aalim, 'total_student': total_student}
    return render(request, "admin_home.html", context)


@login_required(login_url='user_login')
def admin_maktab_page(request):
    all_maktab = Maktab.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        Maktab.objects.create(
            maktab_name=name
        )
        return redirect('maktab_list')
    context = {'maktabs': all_maktab}
    return render(request, "maktab_list.html", context)


@login_required(login_url='user_login')
def admin_syllabus_page(request):
    all_syllabus = Syllabus.objects.all()
    if request.method == "POST":
        subject = request.POST.get("name")
        Syllabus.objects.create(
            subject=subject
        )
        return redirect('syllabus_page')
    context = {'all_syllabus': all_syllabus}
    return render(request, "syllabus_list.html", context)


@login_required(login_url='user_login')
def admin_student_page(request):
    form = StudentForm()
    all_students_obj = Student.objects.all()
    all_maktab_obj = Maktab.objects.all()
    all_student = all_students_obj
    student_id = request.GET.get('select_student')
    try:
        student_id = int(student_id)
    except Exception:
        student_id = None
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_student_page')
        messages.info(request, 'Something went wrong, please try again')
    if 'select_student' in request.GET:
        if student_id:
            all_student = all_student.filter(id=int(student_id))
    pages = Paginator(all_student, 100)
    page_num = request.GET.get('page', 1)
    try:
        page = pages.page(page_num)
    except EmptyPage:
        page = pages.page(1)
    context = {'all_student': page,
               'all_student_obj': all_students_obj,
               'all_maktab': all_maktab_obj,
               'form': form, 'student_id': student_id}
    return render(request, "admin_student_page.html", context)


def admin_maktab_overview(request):
    all_maktab_obj = Maktab.objects.all()
    all_syllabus_obj = Syllabus.objects.all()
    total_syllabus = all_syllabus_obj.count()
    all_syllabus_status_obj = SyllabusStatus.objects.all()
    all_student_obj = Student.objects.all()
    final = []
    for maktab in all_maktab_obj:
        maktab_name = maktab.maktab_name
        temp = {}
        all_student = list(all_student_obj.filter(
            maktab=maktab).values_list('id', flat=True))
        total_student = len(all_student)
        all_syllabus_status = all_syllabus_status_obj.filter(
            student_id__in=all_student)
        completed_course = all_syllabus_status.filter(
            ~Q(start_date=None) & ~Q(end_date=None))
        total_complete_course = completed_course.count()
        incompleted_course = all_syllabus_status.filter(
            ~Q(start_date=None) & Q(end_date=None))
        total_incomplete_course = incompleted_course.count()
        total_syllabus_count = total_syllabus*total_student
        add_course_com_incomp = total_complete_course+total_incomplete_course
        total_notstarted_course = total_syllabus_count-add_course_com_incomp
        temp['maktab_data'] = {"maktab_name": maktab_name,
                               "total_student": total_student,
                               "total_syllabus": total_syllabus_count,
                               "total_complete": total_complete_course,
                               "total_incomplete": total_incomplete_course,
                               "total_notstarted": total_notstarted_course
                               }
        final.append(temp)
    print('final data', final)
    pages = Paginator(final, 100)
    page_num = request.GET.get('page', 1)
    try:
        page = pages.page(page_num)
    except EmptyPage:
        page = pages.page(1)
    context = {"final_data": page}
    return render(request, 'admin_maktab_overview.html', context)


@login_required(login_url='user_login')
def admin_student_rawdata_page(request):
    all_syllabus_status_obj = SyllabusStatus.objects.all()
    all_syllabus_status = all_syllabus_status_obj.order_by('student')
    searched_text = request.GET.get('text')
    maktab_id = request.GET.get('select_maktab')
    try:
        maktab_id = int(maktab_id)
    except Exception:
        maktab_id = None
    try:
        maktab = Maktab.objects.get(id=maktab_id)
    except Exception:
        maktab = None
    if 'text' in request.GET or 'select_maktab' in request.GET:
        if maktab:
            # student_list = list(Student.objects.filter(
            #     maktab=maktab).values_list('id', flat=True))
            all_syllabus_status = all_syllabus_status.filter(
                student__maktab=maktab).order_by('student')
        if searched_text:
            split_text = searched_text.split()
            for text in split_text:
                all_syllabus_status = all_syllabus_status.filter(
                    Q(student__name__icontains=text) |
                    Q(student__father_name__icontains=text) |
                    Q(student__address__icontains=text) |
                    Q(student__aadhaar_number__icontains=text)
                )

    pages = Paginator(all_syllabus_status, 100)
    page_num = request.GET.get('page', 1)
    try:
        page = pages.page(page_num)
    except EmptyPage:
        page = pages.page(1)

    all_maktab = Maktab.objects.all()
    context = {'all_syllabus_status': page,
               'all_maktab': all_maktab,
               'searched_text': searched_text,
               'maktab_id': maktab_id}
    return render(request, "admin_student_overview.html", context)


@login_required(login_url='user_login')
def add_admin_page(request):
    admin_user = UserProfile.objects.filter(user_type='admin')
    if request.method == "POST":
        phone = request.POST.get("phone")
        passcode = request.POST.get("passcode")
        name = request.POST.get("name")
        username = request.POST.get("email")
        try:
            already_user = User.objects.get(username=username)
        except Exception:
            already_user = None
            print('user', already_user)
        if already_user is None:
            new_user = User.objects.create_user(
                username=username, password=passcode, first_name=name)
            UserProfile.objects.create(
                user=new_user,
                phone=phone,
                email=username,
                password=passcode,
                user_type='admin',
            )
            return redirect('admin_team')
        else:
            messages.info(
                request, 'This Email Id is already exist in our DataBase')
            return redirect('admin_team')
    context = {'admin_user': admin_user}
    return render(request, "admin_team.html", context)


@login_required(login_url='user_login')
def admin_aalim_page(request):
    all_aalim = UserProfile.objects.filter(user_type='aalim')
    all_maktab = Maktab.objects.all()
    json_allmaktab = serializers.serialize('json', all_maktab)

    if request.method == "POST":
        phone = request.POST.get("phone")
        passcode = request.POST.get("passcode")
        name = request.POST.get("name")
        username = request.POST.get("email")
        maktabs = request.POST.getlist("maktab")
        # print('judge data', courts)
        try:
            already_user = User.objects.get(username=username)
        except Exception:
            already_user = None
            print('user', already_user)
        if already_user is None:
            new_user = User.objects.create_user(
                username=username, password=passcode, first_name=name)
            aalim_profile = UserProfile.objects.create(
                user=new_user,
                phone=phone,
                email=username,
                password=passcode,
                user_type='aalim',
            )
            aalim_obj = Alim.objects.create(
                user=aalim_profile)
            for maktab in maktabs:
                # each_court = Court.objects.get(id=int(court))
                aalim_obj.maktab.add(maktab)
            return redirect('aalim_list')
        else:
            messages.info(
                request, 'This email Id is already exist in our DataBase')
            return redirect('judges_list')
    context = {'aalims': all_aalim, 'maktabs': all_maktab,
               'json_allmaktab': json_allmaktab}
    return render(request, "aalim_list.html", context)


def recieve_aalim_id(request):
    if request.method == "POST":
        data = json.loads(request.body)
        aalim_id = data["data_obj"]
        # print("data", judge_id)
        aalimProfile = UserProfile.objects.get(id=int(aalim_id))
        profile_json = serializers.serialize('json', [aalimProfile])
        aalim = Alim.objects.filter(user=aalimProfile)
        # print('con', contact)
        aalim_json = serializers.serialize('json', aalim)
        print('judge', aalim_json)
        return JsonResponse({"msg": "success",
                             "name": aalimProfile.user.first_name,
                             "profile_data": json.loads(profile_json),
                             "aalim": json.loads(aalim_json)})
    return render(request, "aalim_list.html")


def edit_aalim(request):
    if request.method == "POST":
        maktab_id = request.POST.getlist("edit_maktab")
        user_id = request.POST.get("edit_id")
        user_data = UserProfile.objects.get(id=int(user_id))
        aalim_data = Alim.objects.get(user=user_data)
        aalim_data.maktab.clear()
        for maktab in maktab_id:
            # each_court = Court.objects.get(id=int(court))
            aalim_data.maktab.add(maktab)
        return redirect('aalim_list')
    context = {}
    return render(request, 'judge_list.html', context)


@login_required(login_url='user_login')
def aalim_home_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    if usertype == 'admin':
        return redirect('admin_page')
    aalim_qs = Alim.objects.get(user=staffProfile)
    my_maktab = aalim_qs.maktab.all()
    all_student_obj = Student.objects.filter(Q(maktab__in=my_maktab))
    all_student = all_student_obj
    searched_text = request.GET.get('text')
    maktab_id = request.GET.get('select_maktab')
    try:
        maktab_id = int(maktab_id)
    except Exception:
        maktab_id = None
    try:
        maktab = Maktab.objects.get(id=int(maktab_id))
    except Exception:
        maktab = None
    if 'text' in request.GET or 'select_maktab' in request.GET:
        if maktab:
            all_student = all_student.filter(maktab=maktab)
        if searched_text:
            split_text = searched_text.split()
            for text in split_text:
                all_student = all_student.filter(
                    Q(name__icontains=text) |
                    Q(father_name__icontains=text) |
                    Q(address__icontains=text) |
                    Q(aadhaar_number__icontains=text)
                )
    pages = Paginator(all_student, 10)
    page_num = request.GET.get('page', 1)
    try:
        page = pages.page(page_num)
    except EmptyPage:
        page = pages.page(1)
    context = {'all_student': page,
               'maktab_list': my_maktab,
               'searched_text': searched_text,
               'maktab_id': maktab_id}
    return render(request, 'aalim_home.html', context)


@login_required(login_url='user_login')
def add_student_page(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    if usertype == 'admin':
        return redirect('admin_page')
    aalim_qs = Alim.objects.get(user=staffProfile)
    maktab_list = aalim_qs.maktab.all()
    print('length', maktab_list)
    form = StudentForm()
    form.fields['maktab'].queryset = maktab_list
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            print('form data', form)
            if maktab_list.count() > 1:
                form.save()
            else:
                new_student = form.save(commit=False)
                new_student.maktab = maktab_list[0]
                new_student.save()
            return redirect('/')
        messages.info(request, 'Something went wrong, please try again')
    context = {'form': form, 'maktab_list': maktab_list}
    return render(request, "student_create_page.html", context)


@login_required(login_url='user_login')
def student_detail_page(request, pk):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    usertype = staffProfile.user_type
    if usertype == 'admin':
        return redirect('admin_page')
    aalim_qs = Alim.objects.get(user=staffProfile)
    maktab_list = aalim_qs.maktab.all()
    student_data = Student.objects.get(id=pk)
    all_syllabus = Syllabus.objects.all()
    all_syllabus_status = SyllabusStatus.objects.filter(student=student_data)
    student_status = {}
    for status in all_syllabus_status:
        subject = status.subject.subject
        subject_id = status.subject.id
        if status.start_date:
            start_date = str(status.start_date)
        else:
            start_date = ''
        if status.end_date:
            end_date = str(status.end_date)
        else:
            end_date = ''
        print('date', start_date, end_date)
        status_id = status.id
        student_status[subject_id] = {
            'status_id': status_id, 'start_date': start_date,
            'end_date': end_date}

    final = []
    for syllabus in all_syllabus:
        temp = {}
        syllabus_id = syllabus.id
        syllabus_name = syllabus.subject
        status_id = 0
        print('syllabus name', syllabus_name)
        try:
            this_syllabus_status = student_status[syllabus_id]
        except:
            this_syllabus_status = None
        if this_syllabus_status:
            status_id = this_syllabus_status['status_id']
        try:
            start_date = student_status[syllabus_id]['start_date']
            print('startdate', str(start_date))
        except:
            start_date = ''
        try:
            end_date = student_status[syllabus_id]['end_date']
        except:
            end_date = ''

        temp = {'s_id': syllabus_id, 'status_id': status_id,
                's_name': syllabus_name,
                's_date': start_date, 'e_date': end_date}
        final.append(temp)

    form = StudentForm(request.POST or None,
                       request.FILES or None, instance=student_data)
    form.fields['maktab'].queryset = maktab_list
    # json_final = json.loads(final)
    print('final', final)
    if request.method == "POST":
        if form.is_valid():
            if maktab_list.count() > 1:
                form.save()
                return redirect('/')
            else:
                edit_student = form.save(commit=False)
                edit_student.maktab = maktab_list[0]
                edit_student.save()
                return redirect('/')
        messages.info(request, 'Something went wrong, please try again')
    # form.fields['case_type'].queryset = CaseType.objects.all()
    context = {'form': form, 'student_data': student_data,
               'maktab_list': maktab_list, 'all_syllabus': all_syllabus,
               'all_syllabus_status': all_syllabus_status,
               'final_data': final,
               'json_final': 'json_final'}
    return render(request, "student_data_page.html", context)


@login_required(login_url='user_login')
def student_syllabus_status(request):
    user = request.user
    staffProfile = UserProfile.objects.get(user=user)
    if request.method == "POST":
        status_id = request.POST.get("status_id")
        print('status type', type(status_id))
        student_id = request.POST.get("student_id")
        try:
            this_student = Student.objects.get(id=int(student_id))
        except Exception:
            this_student = None
        syllabus_id = request.POST.get("syllabus_id")
        try:
            this_syllabus = Syllabus.objects.get(id=int(syllabus_id))
        except Exception:
            this_syllabus = None

        if request.POST.get("start_date"):
            start_date = request.POST.get("start_date")
        else:
            start_date = None
        if request.POST.get("end_date"):
            end_date = request.POST.get("end_date")
        else:
            end_date = None

        print('date', start_date, 'k', end_date)
        if status_id == '0':
            SyllabusStatus.objects.create(
                student=this_student,
                subject=this_syllabus,
                start_date=start_date,
                end_date=end_date
            )
            return redirect('student_detail_page', pk=student_id)
        else:
            this_status = SyllabusStatus.objects.get(id=int(status_id))
            this_status.start_date = start_date
            this_status.end_date = end_date
            this_status.save()
            return redirect('student_detail_page', pk=student_id)

    context = {}
    return render(request, "student_data_page.html", context)
