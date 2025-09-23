from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.shortcuts import render
from .models import Project, ProjectCategory
from django.views.generic import ListView, DetailView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def about(request: HttpRequest) -> HttpResponse:
    # templates/main/about.html
    return render(request, "main/about.html")


def services(request: HttpRequest) -> HttpResponse:
    # templates/main/services.html
    return render(request, "main/services.html")


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
    # templates/main/blog.html
    return render(request, "main/includes/privacy.html")


from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory

from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory

# main/views.py
from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory

# main/views.py
from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory

from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectCategory


def _filtered_projects(request):
    cat_slug = request.GET.get("category")
    qs = Project.objects.prefetch_related("categories").all()
    if cat_slug:
        qs = qs.filter(categories__slug=cat_slug).distinct()
    return qs, cat_slug


def projects(request):
    qs, cat_slug = _filtered_projects(request)
    categories = ProjectCategory.objects.order_by("order", "name")
    return render(request, "main/includes/projects.html", {
        "projects": qs,
        "categories": categories,
        "selected_category": cat_slug,
        "show_filters": True,
    })


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
