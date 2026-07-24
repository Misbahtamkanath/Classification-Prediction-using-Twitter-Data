from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from users.models import UserRegistrationModel

# Create your views here.
def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        # TODO: Replace hardcoded credentials with proper authentication system
        # Security Issue: This is a placeholder. Use Django's built-in authentication.
        if usrid == 'admin' and pswd == 'admin':
            request.session['admin_logged_in'] = True
            request.session['admin_id'] = usrid
            return redirect('AdminHome')
        else:
            messages.error(request, 'Invalid login credentials. Please check your username and password.')
    return render(request, 'AdminLogin.html', {})


def AdminHome(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    return render(request, 'admins/AdminHome.html')


def RegisterUsersView(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    data = UserRegistrationModel.objects.all()
    return render(request,'admins/viewregisterusers.html',{'data':data})


def ActivaUsers(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, 'Please login first')
        return redirect('AdminLogin')
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request,'admins/viewregisterusers.html',{'data':data})