# backoffice/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Portfolio, ImageAsset, PortfolioImage


# --- Inline: Bir portföydeki görseller (sıra verilebilir) ---
class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 0
    autocomplete_fields = ("image",)
    fields = ("image", "preview", "order")
    readonly_fields = ("preview",)
    ordering = ("order", "id")

    def preview(self, obj):
        try:
            url = obj.image.image.url
        except Exception:
            return "—"
        return format_html(
            '<img src="{}" style="height:60px;border-radius:6px;object-fit:cover;">',
            url
        )


# --- Portfolio admin ---
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "images_count", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    inlines = [PortfolioImageInline]

    def images_count(self, obj):
        return obj.images.count()

    images_count.short_description = "Görsel sayısı"


# --- ImageAsset admin ---
@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "linked_portfolios", "created_at")
    search_fields = ("title", "image")
    list_filter = ("portfolios",)
    ordering = ("-created_at",)

    def thumb(self, obj):
        try:
            url = obj.image.url
        except Exception:
            return "—"
        return format_html(
            '<img src="{}" style="height:50px;border-radius:6px;object-fit:cover;">',
            url
        )

    thumb.short_description = "Önizleme"

    def linked_portfolios(self, obj):
        names = [p.name for p in obj.portfolios.all()]
        return ", ".join(names) if names else "—"

    linked_portfolios.short_description = "Portföyler"


# İstersen ayrı kayıt olarak da görünmesini sağla (çoğu zaman gerekmez)
@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "image", "order")
    list_select_related = ("portfolio", "image")
    ordering = ("portfolio__order", "order", "id")
    autocomplete_fields = ("portfolio", "image")


from .models import Showcase, ShowcaseItem  # en üste ekle


class ShowcaseItemInline(admin.TabularInline):
    model = ShowcaseItem
    extra = 0
    autocomplete_fields = ("portfolio",)
    fields = ("portfolio", "limit", "order")
    ordering = ("order", "id")


@admin.register(Showcase)
class ShowcaseAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active", "items_count")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ShowcaseItemInline]
    ordering = ("order", "name")

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = "Portföy adedi"
