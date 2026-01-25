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

    # 🖼️ Grup bazlı görsel yönetimi (Portfolio Manager)
    path("gruplar/", views.group_manager, name="group_manager"),
    path("gruplar/yeni-foy/", views.group_create_portfolio, name="group_create_portfolio"),
    path("gruplar/<int:pid>/yukle/", views.group_upload, name="group_upload"),
    path("gruplar/<int:pid>/sirala/", views.group_save_order, name="group_save_order"),
    path("gruplar/<int:pid>/kaldir/<int:image_id>/", views.group_remove_image, name="group_remove_image"),

    # 🌟 Vitrin (Showcase) Yönetimi (Showcase Manager)
    path("vitrin-yonetimi/", views.showcase_manager, name="showcase_manager"),

    # Vitrin CRUD API'leri
    path("vitrin/create/", views.showcase_create, name="showcase_create"),
    path("vitrin/<int:sid>/update/", views.showcase_update, name="showcase_update"),
    path("vitrin/<int:sid>/delete/", views.showcase_delete, name="showcase_delete"),

    # Vitrin İçerik (ShowcaseItem) API'leri
    path("vitrin/<int:sid>/items/add/", views.showcase_items_add, name="showcase_items_add"),
    path("vitrin/<int:sid>/items/reorder/", views.showcase_items_reorder, name="showcase_items_reorder"),
    path("vitrin/<int:sid>/items/<int:item_id>/update/", views.showcase_item_update, name="showcase_item_update"),
    path("vitrin/<int:sid>/items/<int:item_id>/remove/", views.showcase_item_remove, name="showcase_item_remove"),

    # ⚙️ Test / Ping
    path("ping/", views.ping, name="ping"),

    path('mesajlar/cevapla/<int:msg_id>/', views.send_reply_email, name='send_reply_email'),
]
