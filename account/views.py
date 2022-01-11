from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from account import utils
from account.forms import UserRegistrationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            generated_password = utils.get_random_password()
            new_user.set_password(generated_password)
            new_user.save()
            cd = user_form.cleaned_data
            email_list = []
            email_list.append(cd['email'])
            subject = 'SWTPZ konto użytkownika {} {}'.format(cd['first_name'], cd['last_name'])
            message = 'Konto użytkownika {} {} zostało założone w SWTPZ\nOto dane potrzebne do logowania: \n' \
                      'Login: {}\nHasło: {}'.format(cd['first_name'], cd['last_name'], new_user, generated_password)
            send_mail(subject, message, 'zswtpz@gmail.com', email_list)
            context = {'foo': 'bar'}
            return render(request, 'dashboard/register_complete.html',
                          {'context': context})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'dashboard/registeruser.html',
                      {'user_form': user_form})
