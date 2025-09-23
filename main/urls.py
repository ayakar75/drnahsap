from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),

    # Liste sayfası
    path("projects/", views.projects, name="projects"),

    # Özel yollar: SLUG’dan önce gelmeli!
    path("projects/partial/", views.projects_partial, name="projects_partial"),
    path("projects/grid/", views.projects_grid, name="projects_grid"),  # varsa kullan

    # Detay: en sonda, SLUG ile
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),

    # Diğerleri
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("blog/", views.blog, name="blog"),
    path("blog/details/", views.blog_details, name="blog_details"),
    path("contact/", views.contact, name="contact"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
]
