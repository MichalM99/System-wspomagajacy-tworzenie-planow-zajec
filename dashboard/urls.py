from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('news_view/', views.news_view, name='news_view'),
    path('add_news/', views.add_news, name='add_news'),
    path('delete_news/<int:id>/', views.delete_news, name='delete_news'),
    path('pdf_view_personal/<int:id>/', views.pdf_view_personal, name='pdf_view_personal'),
]