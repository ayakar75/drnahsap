# backoffice/views.py
from __future__ import annotations

import json
from typing import List

from django.contrib import messages as dj_messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.paginator import Paginator
from django.db import transaction
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_GET, require_http_methods, require_POST

# Projenizde varsa iletişim mesajları için (yoksa bu importu silebilirsiniz)
try:
    from main.models import ContactMessage
except Exception:  # main app yoksa
    ContactMessage = None  # type: ignore

# Bu projede artık modeller backoffice içindeyse:
from backoffice.models import Portfolio, ImageAsset, PortfolioImage

User = get_user_model()


# ------------------------------------------------------------------------------
# Kimlik / Oturum
# ------------------------------------------------------------------------------

@require_http_methods(["GET", "POST"])
def admin_login(request: HttpRequest) -> HttpResponse:
    """
    Basit yönetici girişi.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("backoffice:manager_dashboard")

    ctx = {"error": None}
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user and user.is_active and user.is_staff:
            login(request, user)
            return redirect("backoffice:manager_dashboard")
        ctx["error"] = "Kullanıcı adı veya parola hatalı."

    return render(request, "backoffice/login.html", ctx)


@staff_member_required
def admin_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("backoffice:admin_login")


# ------------------------------------------------------------------------------
# Panel / Mesajlar (mevcut sayfalarınızı kullansın diye basit görünümler ekli)
# ------------------------------------------------------------------------------

@staff_member_required
def manager_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Yönetim ana sayfası.
    """
    return render(request, "backoffice/dashboard.html")


@staff_member_required
def messages_list(request: HttpRequest) -> HttpResponse:
    """
    İletişim mesajları listesi (varsa).
    """
    if ContactMessage is None:
        # main app yoksa boş sayfa bas
        return render(request, "backoffice/messages.html", {"page_obj": None})

    qs = ContactMessage.objects.all().order_by("-created_at")
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page") or 1)
    return render(request, "backoffice/messages.html", {"page_obj": page_obj})


# ------------------------------------------------------------------------------
# YENİ: Grup bazlı yönetim (her grup kartında yükle/sırala/kaldır)
# ------------------------------------------------------------------------------

@staff_member_required
def group_manager(request: HttpRequest) -> HttpResponse:
    """
    Tüm aktif portföyleri listeler; her birinde:
      - Dosya seç + Yükle (doğrudan o gruba)
      - Sürükle-bırak ile sıra düzenleme
      - × ile bu gruptan kaldırma
    """
    portfolios = (
        Portfolio.objects.filter(is_active=True)
        .order_by("order", "name")
        .prefetch_related("portfolioimage_set__image")
    )
    return render(request, "backoffice/manager_groups.html", {"portfolios": portfolios})


@staff_member_required
@require_POST
def group_create_portfolio(request: HttpRequest) -> JsonResponse:
    """
    Yeni grup oluştur (varsa aktif et ve adını güncelle).
    """
    name = (request.POST.get("name") or "").strip()
    if not name:
        return JsonResponse({"ok": False, "error": "İsim gerekli."}, status=400)

    slug = slugify(name)
    p, created = Portfolio.objects.get_or_create(
        slug=slug, defaults={"name": name, "order": 0, "is_active": True}
    )
    if not created:
        changed = False
        if not p.is_active:
            p.is_active = True
            changed = True
        if p.name != name:
            p.name = name
            changed = True
        if changed:
            p.save()

    return JsonResponse({"ok": True, "id": p.id, "name": p.name, "created": created})


@staff_member_required
@require_POST
def group_upload(request: HttpRequest, pid: int) -> JsonResponse:
    """
    Seçilen dosyaları doğrudan 'pid' grubuna ekler.
    - Her dosya için ImageAsset oluşturur,
    - PortfolioImage ile bu gruba bağlar (sona ekler).
    """
    files = request.FILES.getlist("files")
    if not files:
        return JsonResponse({"ok": False, "error": "Dosya seçilmedi."}, status=400)

    try:
        portfolio = Portfolio.objects.get(id=pid, is_active=True)
    except Portfolio.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Grup bulunamadı."}, status=404)

    # Sona eklemek için mevcut en büyük order
    last_order = (
            PortfolioImage.objects.filter(portfolio=portfolio)
            .order_by("-order")
            .values_list("order", flat=True)
            .first()
            or 0
    )

    created, linked = 0, 0
    for f in files:
        asset = ImageAsset(title=f.name.rsplit(".", 1)[0])
        asset.image.save(f.name, f, save=True)
        created += 1

        last_order += 1
        PortfolioImage.objects.create(
            portfolio=portfolio, image=asset, order=last_order
        )
        linked += 1

    return JsonResponse({"ok": True, "created": created, "linked": linked})


@staff_member_required
@require_POST
@transaction.atomic
def group_save_order(request: HttpRequest, pid: int) -> JsonResponse:
    """
    Sadece ilgili grubun (pid) sıralamasını günceller.
    request.POST['order'] = "12,7,5,9" gibi image_id dizisi bekler.
    """
    raw = request.POST.get("order") or ""
    try:
        ids: List[int] = [int(x) for x in raw.split(",") if x.strip()]
    except Exception:
        return HttpResponseBadRequest("Geçersiz order verisi")

    # Tamamen temizleme
    if not ids:
        PortfolioImage.objects.filter(portfolio_id=pid).delete()
        return JsonResponse({"ok": True, "cleared": True})

    # Temizle ve yeni sırayla ekle
    PortfolioImage.objects.filter(portfolio_id=pid).delete()
    bulk = [
        PortfolioImage(portfolio_id=pid, image_id=image_id, order=idx)
        for idx, image_id in enumerate(ids)
    ]
    PortfolioImage.objects.bulk_create(bulk, batch_size=1000)
    return JsonResponse({"ok": True, "count": len(bulk)})


@staff_member_required
@require_POST
def group_remove_image(request: HttpRequest, pid: int, image_id: int) -> JsonResponse:
    """
    Sadece bu portföy ile görsel arasındaki bağı kaldırır (dosyayı silmez).
    """
    PortfolioImage.objects.filter(portfolio_id=pid, image_id=image_id).delete()
    return JsonResponse({"ok": True})


# ------------------------------------------------------------------------------
# (Opsiyonel) Basit ping/sağlık kontrolü
# ------------------------------------------------------------------------------

@require_GET
def ping(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"ok": True})


# main/views.py
from django.shortcuts import render, get_object_or_404
from backoffice.models import Showcase, ShowcaseItem, PortfolioImage





from backoffice.models import (
    Portfolio, ImageAsset, PortfolioImage,  # zaten var
    Showcase, ShowcaseItem,  # vitrin modelleri
)


# --------- SAYFA ----------
@staff_member_required
def showcase_manager(request):
    """
    Solda vitrin listesi, sağda seçilen vitrin içeriği:
      - vitrin oluştur/yenile/sil
      - portföy ekle/çıkar
      - sürükle-bırak sırala
      - limit düzenle
    """
    showcases = Showcase.objects.order_by("order", "name").prefetch_related(
        "items__portfolio"
    )
    portfolios = Portfolio.objects.filter(is_active=True).order_by("order", "name")
    # default ilk vitrin ya da query ile seçim
    sid = request.GET.get("sid")
    selected = None
    if sid:
        selected = next((s for s in showcases if str(s.id) == str(sid)), None)
    if not selected and showcases:
        selected = showcases[0]

    return render(
        request,
        "backoffice/showcase_manager.html",
        {"showcases": showcases, "selected": selected, "portfolios": portfolios},
    )


# --------- API: vitrinin CRUD'u ----------
@staff_member_required
@require_POST
def showcase_create(request):
    name = (request.POST.get("name") or "").strip()
    if not name:
        return JsonResponse({"ok": False, "error": "İsim gerekli."}, status=400)
    s = Showcase.objects.create(name=name, slug=slugify(name), is_active=True, order=0)
    return JsonResponse({"ok": True, "id": s.id, "name": s.name})


@staff_member_required
@require_POST
def showcase_update(request, sid: int):
    s = get_object_or_404(Showcase, id=sid)
    if "name" in request.POST:
        name = (request.POST.get("name") or "").strip()
        if not name:
            return JsonResponse({"ok": False, "error": "İsim gerekli."}, status=400)
        s.name = name
        s.slug = slugify(name) or s.slug
    if "is_active" in request.POST:
        s.is_active = request.POST.get("is_active") == "1"
    if "order" in request.POST:
        try:
            s.order = int(request.POST.get("order"))
        except Exception:
            pass
    s.save()
    return JsonResponse({"ok": True})


@staff_member_required
@require_POST
def showcase_delete(request, sid: int):
    Showcase.objects.filter(id=sid).delete()
    return JsonResponse({"ok": True})


# --------- API: item işlemleri ----------
@staff_member_required
@require_POST
def showcase_items_add(request, sid: int):
    """
    Bir vitrinin içine bir veya daha fazla portföy ekle.
    POST: portfolio_ids=1,2,3  & default_limit=12
    """
    s = get_object_or_404(Showcase, id=sid)
    ids_raw = request.POST.get("portfolio_ids") or ""
    try:
        pids = [int(x) for x in ids_raw.split(",") if x.strip()]
    except Exception:
        return HttpResponseBadRequest("Geçersiz portföy listesi")
    default_limit = request.POST.get("default_limit")
    limit = int(default_limit) if (default_limit or default_limit == "0") else None

    last = (ShowcaseItem.objects.filter(showcase=s).order_by("-order").values_list("order", flat=True).first() or 0)
    created = 0
    for pid in pids:
        if ShowcaseItem.objects.filter(showcase=s, portfolio_id=pid).exists():
            continue
        last += 1
        ShowcaseItem.objects.create(showcase=s, portfolio_id=pid, limit=limit, order=last)
        created += 1
    return JsonResponse({"ok": True, "created": created})


@staff_member_required
@require_POST
@transaction.atomic
def showcase_items_reorder(request, sid: int):
    """
    POST: order=item_id1,item_id2,...
    """
    s = get_object_or_404(Showcase, id=sid)
    raw = request.POST.get("order") or ""
    try:
        ids = [int(x) for x in raw.split(",") if x.strip()]
    except Exception:
        return HttpResponseBadRequest("Geçersiz order")

    # sadece bu vitrine ait item'lar
    items = list(ShowcaseItem.objects.filter(showcase=s, id__in=ids))
    by_id = {i.id: i for i in items}
    for idx, iid in enumerate(ids):
        it = by_id.get(iid)
        if it:
            it.order = idx
    ShowcaseItem.objects.bulk_update(items, ["order"])
    return JsonResponse({"ok": True, "count": len(items)})


@staff_member_required
@require_POST
def showcase_item_update(request, sid: int, item_id: int):
    it = get_object_or_404(ShowcaseItem, showcase_id=sid, id=item_id)
    if "limit" in request.POST:
        val = request.POST.get("limit")
        it.limit = int(val) if val != "" else None
    it.save()
    return JsonResponse({"ok": True})


@staff_member_required
@require_POST
def showcase_item_remove(request, sid: int, item_id: int):
    ShowcaseItem.objects.filter(showcase_id=sid, id=item_id).delete()
    return JsonResponse({"ok": True})
