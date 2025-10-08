from django.urls import path
from . import views

app_name = "backoffice"

urlpatterns = [
    # 🔐 Kimlik işlemleri
    path("", views.admin_login, name="admin_login"),
    path("cikis/", views.admin_logout, name="admin_logout"),

    # 🧭 Panel ve Mesajlar
    path("panel/", views.manager_dashboard, name="manager_dashboard"),
    path("mesajlar/", views.messages_list, name="messages_list"),

    # 🖼️ Grup bazlı görsel yönetimi
    path("gruplar/", views.group_manager, name="group_manager"),
    path("gruplar/yeni-foy/", views.group_create_portfolio, name="group_create_portfolio"),
    path("gruplar/<int:pid>/yukle/", views.group_upload, name="group_upload"),
    path("gruplar/<int:pid>/sirala/", views.group_save_order, name="group_save_order"),
    path("gruplar/<int:pid>/kaldir/<int:image_id>/", views.group_remove_image, name="group_remove_image"),

    # ⚙️ Test / Ping
    path("ping/", views.ping, name="ping"),
]
