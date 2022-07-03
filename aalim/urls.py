from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from.views import login_page, logout_user, admin_home, admin_maktab_page, admin_syllabus_page, admin_aalim_page, add_admin_page, aalim_home_page, recieve_aalim_id, edit_aalim, add_student_page, student_detail_page, student_syllabus_status, admin_student_rawdata_page, admin_student_page, admin_maktab_overview

urlpatterns = [
    path('user_login/', login_page, name='user_login'),
    path('user_logout/', logout_user, name='user_logout'),
    path('admin_page/', admin_home, name='admin_page'),
    path('maktab_list/', admin_maktab_page, name='maktab_list'),
    path('syllabus_page/', admin_syllabus_page, name='syllabus_page'),
    path('aalim_list/', admin_aalim_page, name='aalim_list'),
    path('admin_team/', add_admin_page, name='admin_team'),
    path('recieve_aalim_id/', recieve_aalim_id, name='recieve_aalim_id'),
    path('edit_aalim/', edit_aalim, name='edit_aalim'),
    path('', aalim_home_page, name='aalim_home_page'),
    path('add_new_student/', add_student_page, name='add_new_student'),
    path('student_detail_page/<str:pk>/',
         student_detail_page, name='student_detail_page'),
    path('student_syllabus_status', student_syllabus_status,
         name='student_syllabus_status'),
    path('admin_student_rawdata_page', admin_student_rawdata_page,
         name='admin_student_rawdata_page'),
    path('admin_student_page', admin_student_page, name='admin_student_page'),
    path('admin_maktab_overview', admin_maktab_overview,
         name='admin_maktab_overview')


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
