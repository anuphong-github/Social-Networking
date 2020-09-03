from django.shortcuts import render,redirect
from .forms import UserRegister,UserUpdate,ProfileUpdate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'User Registration Successful ! Please Login. ')
            return redirect('login')
    else:
        form = UserRegister()
    return render(request,'users/register.html',{'form':form})

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdate(request.POST, instance = request.user)
        profile_form = ProfileUpdate(request.POST, request.FILES,instance = request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,f'Updated.')
            return redirect('profile')
    else:
        user_form = UserUpdate(instance = request.user)
        profile_form = ProfileUpdate(instance = request.user.profile)

    return render(request,'users/profile.html',{'user_form':user_form,'profile_form':profile_form})
