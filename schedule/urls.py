from django.urls import path
from schedule import views

urlpatterns = [
    path('set_preferences/', views.set_preferences, name='set_preferences'),
]

