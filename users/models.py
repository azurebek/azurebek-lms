from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_username = models.CharField(
        max_length=100,
        help_text="Telegram @username",
        blank=True, null=True
    )
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)

    def __str__(self):
        return self.username

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # Xabar o'qilganmi yoki yo'q

    def __str__(self):
        return f"{self.name} - {self.subject}"