from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
import users.views as usr_views
import admins.views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('index/', TemplateView.as_view(template_name='index.html'), name='index_page'),
    
    # Users views
    path('UserRegister/', usr_views.UserRegisterActions, name='UserRegister'),
    path('UserRegisterActions/', usr_views.UserRegisterActions, name='UserRegisterActions'),
    path('UserLogin/', usr_views.UserLoginCheck, name='UserLogin'),
    path('UserLoginCheck/', usr_views.UserLoginCheck, name='UserLoginCheck'),
    path('UserHome/', usr_views.UserHome, name='UserHome'),
    path('DatasetView/', usr_views.DatasetView, name='DatasetView'),
    path('training/', usr_views.training, name='training'),
    path('prediction/', usr_views.prediction, name='prediction'),
    
    # Admins views
    path('AdminLogin/', admin_views.AdminLoginCheck, name='AdminLogin'),
    path('AdminLoginCheck/', admin_views.AdminLoginCheck, name='AdminLoginCheck'),
    path('AdminHome/', admin_views.AdminHome, name='AdminHome'),
    path('RegisterUsersView/', admin_views.RegisterUsersView, name='RegisterUsersView'),
    path('ActivaUsers/', admin_views.ActivaUsers, name='ActivaUsers'),
]