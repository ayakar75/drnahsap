from datetime import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import ContactMessage
from django.http import HttpRequest, HttpResponse
from backoffice.models import Showcase, ShowcaseItem, Portfolio, PortfolioImage


def projects_main(request):
    qs, cat_slug = _filtered_projects(request)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "main/projects.html", {
        "projects": page_obj.object_list,
        "page_obj": page_obj,
        "categories": ProjectCategory.objects.order_by("order", "name"),
        "selected_category": cat_slug,
    })


def about(request: HttpRequest) -> HttpResponse:
    # templates/main/about.html
    return render(request, "main/about.html")


# main/views.py
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from backoffice.models import Showcase, ShowcaseItem, PortfolioImage

# main/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from backoffice.models import Showcase, ShowcaseItem, PortfolioImage


def services(request: HttpRequest) -> HttpResponse:
    # mevcut sabit içeriklerin (service_cards, process_steps, faqs) sende nasılsa öyle kalsın
    service_cards = [
        {"title": "Mutfak Dolabı", "icon": "bi-house"},
        {"title": "Banyo Dolabı", "icon": "bi-droplet"},
        {"title": "Gardırop & Ray Dolap", "icon": "bi-collection"},
        {"title": "TV Ünitesi", "icon": "bi-tv"},
        {"title": "Kapı Doğrama", "icon": "bi-door-closed"},
        {"title": "Pergola & Veranda", "icon": "bi-tree"},
        {"title": "Ahşap Bahçe Mobilyası", "icon": "bi-flower1"},
        {"title": "Ofis Mobilyası", "icon": "bi-briefcase"},
        {"title": "Merdiven & Korkuluk", "icon": "bi-ladder"},
        {"title": "CNC/Lazer Kesim", "icon": "bi-cpu"},
        {"title": "Tadilat & Restorasyon", "icon": "bi-recycle"},
        {"title": "Özel Tasarım Projeler", "icon": "bi-stars"},
    ]
    process_steps = [
        "Keşif & Ölçü Alma", "Tasarım & 3D Görselleştirme", "Malzeme Seçimi & Teklif",
        "Üretim", "Boya/Vernik", "Montaj & Teslimat", "Garanti & Bakım",
    ]
    faqs = [
        {"q": "Teslim süresi nedir?", "a": "Proje kapsamına göre 10–30 iş günü arasında değişir."},
        {"q": "Keşif/ölçü alma ücretli mi?",
         "a": "Merkez bölge için ücretsiz; uzak lokasyonlarda yol ücreti olabilir."},
        {"q": "Garanti var mı?", "a": "Montaj ve işçilik 2 yıl; donanım üretici garantisi geçerlidir."},
    ]

    # ÖNEMLİ: Artık .first() kullanmıyoruz; TÜM aktif vitrinleri listeliyoruz
    showcases_qs = Showcase.objects.filter(is_active=True).order_by("order", "id")

    # UI’da göstermek için sadece id, ad ve toplam görsel sayısı (opsiyonel)
    showcases = []
    for sc in showcases_qs:
        # vitrindeki portföyleri bul
        port_ids = list(
            ShowcaseItem.objects.filter(showcase=sc).values_list("portfolio_id", flat=True)
        )
        total = PortfolioImage.objects.filter(portfolio_id__in=port_ids).count() if port_ids else 0
        showcases.append({"id": sc.id, "name": sc.name, "total": total})

    return render(request, "main/services.html", {
        "service_cards": service_cards,
        "process_steps": process_steps,
        "faqs": faqs,
        "showcases": showcases,  # ← birden çok vitrin
    })


# AJAX: Bir vitrindeki TÜM portföylerin görsellerini getir (sayfa yenilemeden)
def services_showcase_images(request: HttpRequest, sid: int) -> JsonResponse:
    per = min(max(int(request.GET.get("per", 12)), 1), 60)
    page = max(int(request.GET.get("page", 1)), 1)

    sc = get_object_or_404(Showcase, pk=sid, is_active=True)
    port_ids = list(
        ShowcaseItem.objects.filter(showcase=sc).values_list("portfolio_id", flat=True)
    )

    qs = PortfolioImage.objects.filter(portfolio_id__in=port_ids).select_related("image").order_by(
        "portfolio__order", "order", "id"
    )

    total = qs.count()
    start, end = (page - 1) * per, (page - 1) * per + per
    chunk = qs[start:end]

    data = {
        "ok": True,
        "showcase": {"id": sc.id, "name": sc.name},
        "page": page,
        "per": per,
        "total": total,
        "has_more": end < total,
        "images": [{"url": pi.image.image.url, "title": pi.image.title or sc.name} for pi in chunk],
    }
    return JsonResponse(data)


def blog(request: HttpRequest) -> HttpResponse:
    # templates/main/blog.html
    return render(request, "main/blog.html")


def blog_details(request: HttpRequest) -> HttpResponse:
    # templates/main/blog-details.html
    return render(request, "main/blog-details.html")


def contact(request: HttpRequest) -> HttpResponse:
    """
    Basit POST yakalama. Gerçek hayatta burada e-posta gönderme
    veya veritabanına kaydetme yapılabilir.
    """
    form_data = {}
    sent = False

    if request.method == "POST":
        form_data["name"] = request.POST.get("name", "").strip()
        form_data["email"] = request.POST.get("email", "").strip()
        form_data["message"] = request.POST.get("message", "").strip()
        # TODO: e-posta gönder / DB'ye kaydet / reCAPTCHA vb.
        sent = True

    return render(
        request,
        "main/contact.html",
        {
            "sent": sent,
            "form_data": form_data,
        },
    )


def terms(request: HttpRequest) -> HttpResponse:
    # templates/main/blog.html
    return render(request, "main/includes/terms.html")


def privacy(request: HttpRequest) -> HttpResponse:
    """
       Gizlilik ve verilerin korunması.
       """
    return render(request, "main/privacy.html")


def ownership(request):
    """
    Mülkiyet Hakları sayfası view fonksiyonu.
    """
    context = {
        "current_date": datetime.now().strftime("%B %Y"),  # sayfada 'Son güncelleme tarihi' için
    }
    return render(request, "main/ownership.html", context)


from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory


def _filtered_projects(request):
    cat_slug = request.GET.get("category")
    qs = Project.objects.prefetch_related("categories").all()
    if cat_slug:
        qs = qs.filter(categories__slug=cat_slug).distinct()
    return qs, cat_slug


def projects_partial(request):
    qs, _ = _filtered_projects(request)
    # Yalnız grid parçasını döndür — mevcut include dosyanı kullandık
    return render(request, "main/includes/projects_grid.html", {"projects": qs})


def home(request):
    home_projects = Project.objects.prefetch_related("categories").order_by("-id")[:6]
    categories = ProjectCategory.objects.order_by("order", "name")
    return render(request, "main/index.html", {
        "home_projects": home_projects,
        "projects": home_projects,
        "categories": categories,
        "selected_category": None,
        "show_filters": False,
    })


def project_detail(request, slug):
    project = get_object_or_404(Project.objects.prefetch_related("categories"), slug=slug)
    return render(request, "main/includes/project_details.html", {"project": project})


# (İsteğe bağlı) Sadece ızgara döndüren, AJAX/include amaçlı minimal view.
def projects_grid(request):
    qs = Project.objects.prefetch_related('categories').all()
    category_slug = request.GET.get("category")
    if category_slug:
        qs = qs.filter(categories__slug=category_slug)
    return render(request, "main/includes/projects_grid.html", {
        "projects": qs[:12],  # grid için sınırlı liste
    })


@require_POST
@csrf_protect
def contact_message_api(request):
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    subject = request.POST.get("subject", "").strip()
    message = request.POST.get("message", "").strip()

    errors = {}
    if not name:  errors["name"] = "Ad gerekli."
    if not email: errors["email"] = "E-posta gerekli."
    if not message: errors["message"] = "Mesaj gerekli."
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    ContactMessage.objects.create(
        name=name, email=email, phone=phone, subject=subject, message=message
    )
    return JsonResponse({"ok": True})
