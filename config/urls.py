from django.contrib import admin
from django.urls import path, include, re_path # <--- re_path qo'shildi
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # <--- serve (uzatuvchi) qo'shildi

# Users app'idan viewlarni import qilamiz
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

    # 4. Foydalanuvchi tizimi
    path("accounts/", include("users.urls")),

    # 5. Blog tizimi
    path("blog/", include("blog.urls")),

    # 6. KURSLAR TIZIMI
    path("courses/", include("courses.urls")),

    # 👇 ENG MUHIM QISM: RASMLAR UCHUN (Serverda ham ishlashi uchun)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# Agar lokal kompyuterda bo'lsa, oddiy static usulini ham qo'shib qo'yamiz (zarari yo'q)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)