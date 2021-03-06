from django.urls import path

from schedule import views

urlpatterns = [
    path('set_preferences/', views.set_preferences, name='set_preferences'),
    path('schedule/set_preferences/delete/<int:id>/', views.delete_availability, name='delete_availability'),
    path('yg_management/', views.year_group_management, name='yg_management'),
    path('add_year/', views.add_year, name='add_year'),
    path('add_group/<int:id>/', views.add_group, name='add_group'),
    path('manage_year/<int:id>/', views.manage_year, name='manage_year'),
    path('manage_year/<int:pk>/delete/<int:id>/', views.delete_group, name='delete_group'),
    path('yg_management/delete/<int:id>/', views.delete_year, name='delete_year'),
    path('manage_room/', views.manage_room, name='manage_room'),
    path('manage_room/delete/<int:id>/', views.delete_room, name='delete_room'),
    path('manage_room/edit_room/<int:id>/', views.edit_room, name='edit_room'),
    path('manage_schedule/create_schedule/<int:id>/', views.create_schedule, name='create_schedule'),
    path('manage_schedule/delete/<int:pk>/', views.delete_schedule, name='delete_schedule'),
    path('manage_schedule/delete_schedule_item/<int:id>/', views.delete_schedule_item, name='delete_schedule_item'),
    path('manage_year/<int:pk>/delete_lecture/<int:id>/', views.delete_lecture, name='delete_lecture'),
    path('schedule_view/<int:id>/', views.schedule_view, name='schedule_view'),
    path('pdf_view/<int:id>/', views.pdf_view, name='pdf_view'),
    path('external_schedule_view/<int:id>/', views.external_schedule_view, name='external_schedule_view'),
]

