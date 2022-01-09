from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'login-input', 'placeholder': 'Nazwa użytkownika'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'login-input',
            'placeholder': 'Hasło',
        }
))
