from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render

from account import utils
from account.forms import (ProfileEditForm, UserEditForm, UserLoginForm,
                           UserRegistrationForm)

from .models import Profile


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            generated_password = utils.get_random_password()
            new_user.set_password(generated_password)
            new_user.save()
            Profile.objects.create(user=new_user)
            cd = user_form.cleaned_data
            email_list = []
            email_list.append(cd['email'])
            subject = 'SWTPZ konto użytkownika {} {}'.format(cd['first_name'], cd['last_name'])
            message = 'Konto użytkownika {} {} zostało założone w SWTPZ\nOto dane potrzebne do logowania: \n' \
                      'Login: {}\nHasło: {}'.format(cd['first_name'], cd['last_name'], new_user, generated_password)
            send_mail(subject, message, 'zswtpz@gmail.com', email_list)
            return render(request, 'dashboard/register_complete.html',
                          {})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'dashboard/registeruser.html',
                      {'user_form': user_form})


def register_many_users(request):
    return render(request, 'dashboard/registeruser.html',
                      {})



@login_required
def edit_profile(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request,
                  'account/account_details.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})




