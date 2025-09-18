from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quote-submit/", views.quote_submit, name="quote-submit"),
    # Menüde kullanılan sayfalar
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("projects/", views.projects, name="projects"),
    path("team/", views.team, name="team"),
    path("contact/", views.contact, name="contact"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("404/", views.not_found, name="not-found"),

    # Dropdown sayfaları
    path("service-details/", views.service_details, name="service-details"),
    path("project-details/", views.project_details, name="project-details"),

]
