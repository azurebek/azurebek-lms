from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

# Users app'idan viewlarni import qilamiz (Contact page uchun kerak)
from users import views as user_views

# Asosiy sahifa (Home)
def home(request):
    return render(request, "landing.html")

urlpatterns = [
    # 1. Admin panel
    path('admin/', admin.site.urls),

    # 2. Asosiy sahifa
    path("", home, name="home"),

    # 3. Contact sahifasi
    path('contact/', user_views.contact_page, name='contact'),

    # 4. Foydalanuvchi tizimi (Login, Register, Dashboard)
    path("accounts/", include("users.urls")),

    # 5. Blog tizimi
    path("blog/", include("blog.urls")),

    # 6. KURSLAR TIZIMI (YANGI QO'SHILDI) 🎓
    # Bu qator courses/urls.py fayliga ulaydi
    path("courses/", include("courses.urls")),
]

# Media fayllar (Rasm yuklash) uchun sozlama (faqat DEBUG rejimda)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)