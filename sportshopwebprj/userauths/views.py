from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings


User = settings.AUTH_USER_MODEL

def register_view(request):
    if request.method == 'POST': 
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hey {username}!, your account was created successfully!')
            new_user = authenticate(username=form.cleaned_data.get('email'),
                                    password=form.cleaned_data.get('password1'))
            login(request, new_user)
            return redirect('core:index')

    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }

    return render(request, 'userauths/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, f'User with email {email} does not exist.')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('core:index')
        else:
            messages.warning(request, 'Invalid email or password.')

    context = {

    }

    return render(request, 'userauths/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('core:index')
