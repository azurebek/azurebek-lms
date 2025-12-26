from django.contrib import admin
from .models import User, ContactMessage

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Admin panelda foydalanuvchilar ro'yxatida ko'rinadigan ustunlar
    list_display = ("username", "email", "telegram_username", "is_staff", "is_active")
    search_fields = ("username", "email", "telegram_username")
    list_filter = ("is_staff", "is_active")

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
    # Xabarlar tahrirlanmasligi uchun (faqat o'qish uchun)
    readonly_fields = ('created_at',)