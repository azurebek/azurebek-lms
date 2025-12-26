from django.db import models
from django.conf import settings  # <--- MUHIM O'ZGARISH (User o'rniga settings chaqiramiz)
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator


# ==========================================
# 0. PROMOKOD MODELI
# ==========================================
class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Promokod (Masalan: NAVRUZ2025)")
    discount_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Chegirma foizi (%)"
    )
    valid_from = models.DateTimeField(verbose_name="Amal qilish boshlanishi")
    valid_to = models.DateTimeField(verbose_name="Amal qilish tugashi")
    active = models.BooleanField(default=True, verbose_name="Aktivmi?")

    allowed_courses = models.ManyToManyField('Course', blank=True, verbose_name="Qaysi kurslarga amal qiladi?")

    def __str__(self):
        return f"{self.code} (-{self.discount_percentage}%)"

    class Meta:
        verbose_name = "Promokod"
        verbose_name_plural = "Promokodlar"


# ==========================================
# 1. KURS MODELI
# ==========================================
class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Kurs nomi")
    slug = models.SlugField(unique=True, help_text="URL uchun nom")
    description = RichTextField(verbose_name="Kurs haqida batafsil")
    image = models.ImageField(upload_to='courses/', verbose_name="Kurs rasmi")

    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Hozirgi narxi (Sotuvdagi)")
    old_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True,
                                    verbose_name="Eski narxi (Chegirma uchun)")

    telegram_group_link = models.URLField(blank=True, null=True, verbose_name="Yopiq Guruh Linki")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_discount_percent(self):
        if self.old_price and self.old_price > self.price:
            percent = 100 - (self.price * 100 / self.old_price)
            return int(percent)
        return 0

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"


# ==========================================
# 2. DARS MODELI
# ==========================================
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200, verbose_name="Dars mavzusi")
    slug = models.SlugField(help_text="URL uchun")
    order = models.PositiveIntegerField(default=1, verbose_name="Dars raqami")
    video_link = models.URLField(verbose_name="Video Dars Linki (Telegram)")
    content = RichTextField(verbose_name="Dars matni va Qoidalar", blank=True)
    homework_description = RichTextField(verbose_name="Uyga vazifa sharti", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"

    def __str__(self):
        return f"{self.order}-dars: {self.title}"


# ==========================================
# 3. A'ZOLIK VA TO'LOV (FIXED)
# ==========================================
class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Tekshirilmoqda'),
        ('active', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
    )

    # O'ZGARISH SHU YERDA: settings.AUTH_USER_MODEL ishlatildi
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    payment_receipt = models.ImageField(upload_to='receipts/', verbose_name="To'lov cheki", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")

    used_promocode = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True,
                                       verbose_name="Ishlatilgan Promokod")
    final_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True,
                                      verbose_name="To'langan summa")

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "A'zolik (To'lov)"
        verbose_name_plural = "A'zolar va To'lovlar"

    def __str__(self):
        # user.username ishlamasligi mumkin agar custom user bo'lsa, shuning uchun user o'zini qaytaramiz
        return f"{self.user} - {self.course.title}"


# ==========================================
# 4. UYGA VAZIFA (FIXED)
# ==========================================
class HomeworkSubmission(models.Model):
    # O'ZGARISH SHU YERDA: settings.AUTH_USER_MODEL ishlatildi
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='homeworks')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='homeworks/', blank=True, null=True, verbose_name="Vazifa fayli")
    text_answer = models.TextField(blank=True, null=True, verbose_name="Yozma javob")
    is_approved = models.BooleanField(default=False, verbose_name="Qabul qilindimi?")
    admin_comment = models.TextField(blank=True, null=True, verbose_name="O'qituvchi izohi")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vazifa Javobi"
        verbose_name_plural = "Vazifa Javoblari"
        unique_together = ('user', 'lesson')

    def __str__(self):
        status = "✅" if self.is_approved else "⏳"
        return f"{status} {self.user} - {self.lesson.title}"