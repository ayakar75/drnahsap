from django.db import models
from django.utils.text import slugify


class Portfolio(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self): return self.name


class ImageAsset(models.Model):
    """
    Static altında duran görselin göreli yolu (ör: 'assets/portfolio_pool/m1.webp')
    """
    title = models.CharField(max_length=150, blank=True)
    static_path = models.CharField(max_length=300, unique=True)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔑 Aynı görseli birden çok portföyde göstermek için M2M (through ile)
    portfolios = models.ManyToManyField(
        Portfolio, through="PortfolioImage", related_name="images", blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title or self.static_path


class PortfolioImage(models.Model):
    """
    Köprü tablo: Hangi görsel hangi portföyde ve (istersen) hangi sırada?
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    image = models.ForeignKey(ImageAsset, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("portfolio", "image"),)
        ordering = ["portfolio__order", "order", "id"]

    def __str__(self):
        return f"{self.portfolio} · {self.image}"
