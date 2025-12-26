from django.contrib import admin
from .models import Course, Lesson, Enrollment, HomeworkSubmission, PromoCode


# ==========================================
# 1. PROMOKODLAR (ADMIN)
# ==========================================
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'active', 'valid_to')
    list_filter = ('active',)
    search_fields = ('code',)


# ==========================================
# 2. KURSLAR (ADMIN)
# ==========================================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'old_price', 'created_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


# ==========================================
# 3. DARSLAR (ADMIN)
# ==========================================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'course', 'created_at')
    list_filter = ('course',)  # Eng muhimi: Kurs bo'yicha filtrlaydi
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('course', 'order')  # Kurs va raqami bo'yicha tartiblaydi


# ==========================================
# 4. A'ZOLIK VA TO'LOVLAR (ADMIN)
# ==========================================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    # Ro'yxatda nimalar ko'rinsin?
    list_display = ('user', 'course', 'status', 'final_price', 'used_promocode', 'enrolled_at')

    # Nimalar bo'yicha filtrlab bo'lsin?
    list_filter = ('status', 'course', 'used_promocode')

    # Qidiruv (User ismi yoki familiyasi bo'yicha)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    # Eng muhimi: Ro'yxatni o'zidan turib statusni o'zgartirish (Active qilish)
    list_editable = ('status',)

    # Sana bo'yicha navigatsiya
    date_hierarchy = 'enrolled_at'


# ==========================================
# 5. UYGA VAZIFA JAVOBLARI (ADMIN)
# ==========================================
@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_approved', 'submitted_at')

    # lesson__course orqali vazifani qaysi kursga tegishli ekanini filtrlaymiz
    list_filter = ('is_approved', 'lesson__course')

    # Ro'yxatni o'zidan turib "Qabul qilindi" (True) qilish
    list_editable = ('is_approved',)

    search_fields = ('user__username', 'lesson__title')