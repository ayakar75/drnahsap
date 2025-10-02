from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .forms import ManagerLoginForm
from main.models import ContactMessage  # ContactMessage ana app’indeyse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

User = get_user_model()


@require_http_methods(["GET", "POST"])
def manager_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("backoffice:manager_dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # email’den staff kullanıcıyı bul
        user = User.objects.filter(email__iexact=email, is_active=True, is_staff=True).first()
        if user:
            authed = authenticate(request, username=user.get_username(), password=password)
            if authed is not None:
                login(request, authed)
                return redirect("backoffice:manager_dashboard")

        messages.error(request, "E-posta veya şifre hatalı.")

    return render(request, "backoffice/login.html")


def manager_logout(request):
    logout(request)
    return redirect("backoffice:manager_login")


@staff_member_required
def manager_dashboard(request):
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    return render(request, "backoffice/dashboard.html", {"unread_count": unread_count})


# backoffice/views.py

from django.core.paginator import Paginator


@staff_member_required
def manager_dashboard(request):
    from main.models import ContactMessage
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    total_count = ContactMessage.objects.count()
    return render(request, "backoffice/dashboard.html", {
        "unread_count": unread_count,
        "total_count": total_count,
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from main.models import ContactMessage  # modelin burada


@staff_member_required
def manager_dashboard(request):
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    total_count = ContactMessage.objects.count()
    return render(request, "backoffice/dashboard.html", {
        "unread_count": unread_count,
        "total_count": total_count,
    })


@staff_member_required
def manager_messages(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all")  # all | unread | read

    qs = ContactMessage.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(message__icontains=q)

    if status == "unread":
        qs = qs.filter(is_read=False)
    elif status == "read":
        qs = qs.filter(is_read=True)

    # Hızlı işaretleme
    mark_read_id = request.GET.get("okundu")
    mark_unread_id = request.GET.get("okunmadi")
    if mark_read_id:
        ContactMessage.objects.filter(id=mark_read_id).update(is_read=True)
        return redirect(f"{request.path}?status={status}&q={q}")
    if mark_unread_id:
        ContactMessage.objects.filter(id=mark_unread_id).update(is_read=False)
        return redirect(f"{request.path}?status={status}&q={q}")

    counts = {
        "all": ContactMessage.objects.count(),
        "unread": ContactMessage.objects.filter(is_read=False).count(),
        "read": ContactMessage.objects.filter(is_read=True).count(),
    }

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "backoffice/messages.html", {
        "q": q,
        "status": status,
        "counts": counts,
        "page_obj": page_obj,
    })


@staff_member_required
@require_http_methods(["GET", "POST"])
def manager_upload(request):
    uploaded_url = None
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        path = default_storage.save(f"manager_uploads/{f.name}", ContentFile(f.read()))
        uploaded_url = default_storage.url(path)
        messages.success(request, "Dosya yüklendi.")
    return render(request, "backoffice/upload.html", {"uploaded_url": uploaded_url})
