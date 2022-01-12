from django.urls import path
from schedule import views

urlpatterns = [
    path('set_preferences/', views.set_preferences, name='set_preferences'),
    path('schedule/set_preferences/delete/<int:id>/', views.delete_availability, name='delete_availability')
]

