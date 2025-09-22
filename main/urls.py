from django.urls import path
from . import views

app_name = "main"  # namespace için (önerilir)
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('projects/', views.projects, name='projects'),
    path('blog/', views.blog, name='blog'),
    path('blog/details/', views.blog_details, name='blog_details'),
    path('projects/details/', views.project_details, name='project_details'),
    path('contact/', views.contact, name='contact'),
path('terms/', views.terms, name='terms'),
path('privacy/', views.privacy, name='privacy'),


]
