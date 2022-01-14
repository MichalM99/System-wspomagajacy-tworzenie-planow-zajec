from django.urls import path
from schedule import views

urlpatterns = [
    path('set_preferences/', views.set_preferences, name='set_preferences'),
    path('schedule/set_preferences/delete/<int:id>/', views.delete_availability, name='delete_availability'),
    path('yg_management/', views.year_group_management, name='yg_management'),
    path('add_year/', views.add_year, name='add_year'),
    path('add_group/<int:id>/', views.add_group, name='add_group'),
    path('manage_year/<int:id>/', views.manage_year, name='manage_year'),
]

