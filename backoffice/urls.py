from django.urls import path
from . import views

app_name = "backoffice"
urlpatterns = [
    path("", views.manager_login, name="manager_login"),
    path("cikis/", views.manager_logout, name="manager_logout"),
    path("panel/", views.manager_dashboard, name="manager_dashboard"),
    path("mesajlar/", views.manager_messages, name="manager_messages"),
    path("yukle/", views.manager_upload, name="manager_upload"),
]
