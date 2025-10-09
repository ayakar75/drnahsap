from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),

    # Tam sayfa liste
    path("projects/", views.projects_main, name="projects"),

    # Parça/AJAX uçları (liste grid’i vs.)
    path("projects/partial/", views.projects_partial, name="projects_partial"),
    path("projects/grid/", views.projects_grid, name="projects_grid"),

    # Detay — slug en sonda
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),

    # Diğer sayfalar
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("services/portfolio/<int:sid>/images/", views.services_showcase_images, name="services_showcase_images"),
    path("blog/", views.blog, name="blog"),
    path("blog/details/", views.blog_details, name="blog_details"),
    path("contact/", views.contact, name="contact"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("ownership/", views.ownership, name="ownership"),  # 👈 Yeni eklendi
    path("contact/submit/", views.contact_message_api, name="contact_message_api"),
]
