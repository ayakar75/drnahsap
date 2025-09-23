# models.py
import uuid
from django.db import models
from django.utils.text import slugify


class ProjectCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon_class = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=150)
    short_description = models.CharField(max_length=200, blank=True)
    cover = models.ImageField(upload_to="projects/covers/", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    categories = models.ManyToManyField(ProjectCategory, related_name="projects", blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)

    def isotope_classes(self):
        cats = list(self.categories.all())
        return " ".join([c.isotope_class for c in cats]) if cats else "filter-uncategorized"

    # Kapak yoksa final/render görsellerinden biriyle otomatik düşmek için:
    @property
    def effective_cover(self):
        if self.cover:
            return self.cover
        img = (self.images.filter(kind__in=[ProjectImage.Kind.FINAL, ProjectImage.Kind.RENDER], is_active=True)
               .order_by("order", "id").first()) or \
              (self.images.filter(is_active=True).order_by("order", "id").first())
        return img.image if img else None


def project_gallery_upload_to(instance, filename):
    # projects/<slug>/gallery/<uuid>.<ext>
    ext = filename.split(".")[-1].lower()
    base = instance.project.slug or "unassigned"
    return f"projects/{base}/gallery/{uuid.uuid4().hex}.{ext}"


class ProjectImage(models.Model):
    class Kind(models.TextChoices):
        BEFORE = "before", "Öncesi"
        AFTER = "after", "Sonrası"
        DURING = "during", "Uygulama"
        FINAL = "final", "Final"
        RENDER = "render", "Render"
        OTHER = "other", "Diğer"

    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=project_gallery_upload_to)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.OTHER)
    title = models.CharField(max_length=150, blank=True)
    alt_text = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Öncesi–sonrası ikililerini eşleştirmek için aynı anahtar:
    pair_key = models.CharField(
        max_length=50, blank=True,
        help_text="Aynı anahtardaki BEFORE & AFTER görselleri slider'da eşleşir (örn: 'mutfak-1')."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.project.title} | {self.get_kind_display()} | {self.title or self.image.name}"


# Projede eşleşmiş before/after çiftleri (template’te kolay kullanım için)
def before_after_pairs(self):
    pairs = {}
    qs = self.images.filter(is_active=True, pair_key__gt="",
                            kind__in=[ProjectImage.Kind.BEFORE, ProjectImage.Kind.AFTER])
    for img in qs:
        d = pairs.setdefault(img.pair_key, {})
        d[img.kind] = img
    return [(d.get(ProjectImage.Kind.BEFORE), d.get(ProjectImage.Kind.AFTER))
            for _, d in pairs.items() if d.get(ProjectImage.Kind.BEFORE) and d.get(ProjectImage.Kind.AFTER)]


# Project içine helper'ı enjekte edelim (istersen method olarak da ekleyebilirsin)
Project.before_after_pairs = before_after_pairs
