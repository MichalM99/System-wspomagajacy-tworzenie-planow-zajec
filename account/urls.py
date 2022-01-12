from django.urls import path
from django.contrib.auth import views as auth_views
from account.forms import UserLoginForm
from account import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(authentication_form=UserLoginForm, redirect_authenticated_user=True), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password_change_done',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('dashboard/register/', views.register, name='register'),
    path('account/account_details/', views.edit_profile, name='account_details'),
]

