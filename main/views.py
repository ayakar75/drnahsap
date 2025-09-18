from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.shortcuts import render


from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def home(request: HttpRequest) -> HttpResponse:
    # templates/main/index.html
    return render(request, "main/index.html")


def about(request: HttpRequest) -> HttpResponse:
    # templates/main/about.html
    return render(request, "main/about.html")


def services(request: HttpRequest) -> HttpResponse:
    # templates/main/services.html
    return render(request, "main/services.html")


def projects(request: HttpRequest) -> HttpResponse:
    # templates/main/projects.html
    return render(request, "main/projects.html")


def project_details(request: HttpRequest) -> HttpResponse:
    # templates/main/project-details.html
    return render(request, "main/project-details.html")


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