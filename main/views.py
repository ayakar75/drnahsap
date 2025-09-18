from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages


def home(request):
    return render(request, "main/index.html")


# Basit sayfalar (şimdilik boş şablonlar gösterecek)
def about(request):             return render(request, "main/about.html")


def services(request):          return render(request, "main/services.html")


def projects(request):          return render(request, "main/projects.html")


def team(request):              return render(request, "main/team.html")


def contact(request):           return render(request, "main/contact.html")


def service_details(request):   return render(request, "main/service_details.html")


def project_details(request):   return render(request, "main/project_details.html")


def terms(request):             return render(request, "main/terms.html")


def privacy(request):           return render(request, "main/privacy.html")


def not_found(request):         return render(request, "main/404.html", status=404)


@require_POST
def quote_submit(request):
    # Honeypot (bot filtresi)
    if request.POST.get("website"):
        messages.error(request, "Invalid submission.")
        return redirect("home")

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    message = request.POST.get("message", "").strip()

    if not name or not email or not message:
        messages.error(request, "Please fill the required fields.")
        return redirect("home")

    # TODO: e-posta gönder veya DB'ye kaydet
    messages.success(request, "Your quote request has been sent successfully. Thank you!")
    return redirect("home")
