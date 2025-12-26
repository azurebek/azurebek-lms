from django.db import models
from django.conf import settings
from django.utils.text import slugify
from ckeditor.fields import RichTextField  # <--- 1. IMPORT QILAMIZ


# Category modeli o'zgarishsiz qoladi...
class Category(models.Model):
    # ... (bu yerga tegmang) ...
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    # ... (tepadagi qismlar o'sha-o'sha) ...
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    # --- O'ZGARISH SHU YERDA ---
    content = RichTextField()  # TextField() o'rniga RichTextField() bo'ldi
    # ---------------------------

    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField() # Izoh matni
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True) # Admin o'chirib qo'yishi mumkin

    class Meta:
        ordering = ['created_at'] # Eskilari tepada, yangilari pastda

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"