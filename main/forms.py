# main/forms.py
from django import forms
from .models import ProjectCategory

class ProjectCategoryAdminForm(forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = "__all__"
