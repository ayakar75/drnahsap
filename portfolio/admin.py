from django.contrib import admin
from django.utils.html import format_html
from .models import Portfolio, ImageAsset, PortfolioImage


class PortfolioImageInline(admin.TabularInline):
    """
    Portfolio sayfasında: mevcut görselleri arayıp ekle, order ver.
    """
    model = PortfolioImage
    extra = 0
    autocomplete_fields = ("image",)
    fields = ("image", "preview", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.image_id:
            return format_html('<img src="/static/{}" style="height:50px;border-radius:4px;object-fit:cover;">',
                               obj.image.static_path)
        return "-"


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PortfolioImageInline]


@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "static_path", "linked_portfolios", "created_at")
    search_fields = ("title", "static_path", "tags")
    list_filter = ("portfolios",)
    ordering = ("-created_at",)

    def thumb(self, obj):
        return format_html('<img src="/static/{}" style="height:40px;border-radius:4px;object-fit:cover;">',
                           obj.static_path)

    thumb.short_description = "Önizleme"

    def linked_portfolios(self, obj):
        names = [p.name for p in obj.portfolios.all()]
        return ", ".join(names) if names else "—"

    linked_portfolios.short_description = "Portföyler"
