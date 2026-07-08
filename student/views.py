from django.shortcuts import render,redirect
from .models import Student,Department 
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings


def google_signin_enabled():
    return bool(
        getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
        and getattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', '')
    )






def logout(request):
    auth.logout(request)
    messages.success(request,'Logout successful')
    return redirect('library_home')


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(request,
                                 username=request.POST['studentID'], 
                                 password=request.POST['password'])
        print(user)                        
        if user is None:
            messages.error(request,'Invalid CREDENTIALS')
            return redirect('/aeclibrary/student/login/')
        else:
            auth.login(request, user)
            messages.success(request,'Login successful')
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            return redirect('library_home')
    else:
        return render(request, 'student/login.html', {
            'google_signin_enabled': google_signin_enabled(),
        })


def signup(request):
    
    if request.method=='POST':
        try:
            user=User.objects.get(username=request.POST['studentID'])
            messages.success(request,'user exists already !!')
            return redirect('/aeclibrary/student/login/')
            

        except User.DoesNotExist:
            user=User.objects.create_user(username=request.POST['studentID'],password=request.POST['password'])

            newstudent=Student.objects.create(first_name=request.POST['firstname'],last_name=request.POST['lastname'],
            department=Department.objects.get(id=request.POST['department']),student_id=user
            )

            auth.login(request,user)
            messages.success(request,'Signup successful')
            if "next" in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('library_home')

    else:
        return render(request,'student/signup.html',{
            "departments":Department.objects.all(),
            "users":list(User.objects.values_list('username',flat=True)),
            "google_signin_enabled": google_signin_enabled(),
        })

