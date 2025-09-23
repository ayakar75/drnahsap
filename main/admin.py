# main/admin.py
from django.contrib import admin

# Modeller
try:
    # Projende ProjectImage yoksa bu import hata vermesin diye try/except kullanıyoruz
    from .models import Project, ProjectCategory, ProjectImage  # type: ignore
except ImportError:
    from .models import Project, ProjectCategory  # type: ignore

    ProjectImage = None  # type: ignore

# Formlar
# forms.py içinde ProjectCategoryAdminForm tanımlı olmalı
from .forms import ProjectCategoryAdminForm

# --- Inlines ---------------------------------------------------------------
if ProjectImage:
    class ProjectImageInline(admin.TabularInline):
        model = ProjectImage
        extra = 1
        fields = ("image", "alt_text", "order", "is_active")
        ordering = ("order",)
        classes = ("collapse",)
else:
    ProjectImageInline = None  # type: ignore


# --- Admin'ler -------------------------------------------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "category_list")
    search_fields = ("title", "short_description")
    list_filter = ("categories",)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    readonly_fields = ()
    ordering = ("title",)

    if ProjectImageInline:
        inlines = [ProjectImageInline]

    @admin.display(description="Kategoriler")
    def category_list(self, obj):
        # Admin liste görünümünde ilişikli kategorileri virgülle göster
        return ", ".join(c.name for c in obj.categories.all())


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    form = ProjectCategoryAdminForm  # dropdown vb. özelleştirmeler bu formdan gelecek
    list_display = ("name", "slug", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
