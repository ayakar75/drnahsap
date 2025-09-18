from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.shortcuts import render


def home(request):     return render(request, 'index.html')


def about(request):    return render(request, 'about.html')


def services(request): return render(request, 'services.html')


def projects(request): return render(request, 'projects.html')


def blog(request):     return render(request, 'blog.html')


def contact(request):  return render(request, 'contact.html')
