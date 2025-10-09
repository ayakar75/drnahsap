from django.db import models
from django.utils.text import slugify
from datetime import datetime


def portfolio_image_upload_to(instance, filename):
    y = datetime.now().strftime("%Y")
    m = datetime.now().strftime("%m")
    base, ext = filename.rsplit(".", 1)
    safe = slugify(base) or "image"
    return f"portfolio_pool/{y}/{m}/{safe}.{ext.lower()}"


class Portfolio(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "portfolio"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ImageAsset(models.Model):
    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to=portfolio_image_upload_to)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # bir görsel birden çok portföyde olabilir
    portfolios = models.ManyToManyField(
        Portfolio, through="PortfolioImage", related_name="images", blank=True
    )

    class Meta:
        db_table = "image_asset"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.image.name


class PortfolioImage(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    image = models.ForeignKey(ImageAsset, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "portfolio_image_link"
        unique_together = (("portfolio", "image"),)
        ordering = ["portfolio__order", "order", "id"]

    def __str__(self):
        return f"{self.portfolio} · {self.image}"


# === vitrinde kullanılacak koleksiyonlar ===
class Showcase(models.Model):
    name = models.CharField(max_length=120, unique=True)  # örn: "Masa ve Sandalye Portföyü"
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "service_showcase"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ShowcaseItem(models.Model):
    showcase = models.ForeignKey(Showcase, on_delete=models.CASCADE, related_name="items")
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)  # vitrindeki sırası
    limit = models.PositiveSmallIntegerField(null=True, blank=True)  # bu portföyden kaç görsel? (boş=hepsi)

    class Meta:
        db_table = "service_showcase_item"
        unique_together = (("showcase", "portfolio"),)
        ordering = ["showcase__order", "order", "id"]

    def __str__(self):
        return f"{self.showcase} · {self.portfolio}"
