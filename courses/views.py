from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

# Barcha kerakli modellar
from .models import Course, Lesson, Enrollment, HomeworkSubmission, PromoCode
# Barcha kerakli formalar
from .forms import EnrollmentForm, HomeworkForm


# ==========================================
# 1. BARCHA KURSLAR RO'YXATI (VITRINA)
# ==========================================
def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    context = {
        'courses': courses
    }
    return render(request, 'courses/course_list.html', context)


# ==========================================
# 2. KURS HAQIDA BATAFSIL (DETAIL) + LEADERBOARD
# ==========================================
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    # --- 1. User kursga a'zomi? ---
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course, status='active').exists()

    # --- 2. Darslar ro'yxati va Qulflarni hisoblash ---
    lessons = list(course.lessons.all().order_by('order'))
    for lesson in lessons:
        if is_enrolled:
            if lesson.order == 1:
                lesson.is_locked = False
            else:
                prev_lesson = course.lessons.filter(order=lesson.order - 1).first()
                if prev_lesson:
                    has_approval = HomeworkSubmission.objects.filter(
                        user=request.user,
                        lesson=prev_lesson,
                        is_approved=True
                    ).exists()
                    lesson.is_locked = not has_approval
                else:
                    lesson.is_locked = False
        else:
            lesson.is_locked = True

    # --- 3. REYTING (LEADERBOARD) MANTIQLARI ---
    # Shu kursga faol a'zo bo'lganlarni olamiz
    active_enrollments = Enrollment.objects.filter(course=course, status='active')
    total_lessons_count = course.lessons.count()

    leaderboard_data = []
    for enroll in active_enrollments:
        # Foydalanuvchining tasdiqlangan vazifalari soni
        approved_homeworks = HomeworkSubmission.objects.filter(
            user=enroll.user,
            lesson__course=course,
            is_approved=True
        ).count()

        # Foizni hisoblash
        if total_lessons_count > 0:
            progress = int((approved_homeworks / total_lessons_count) * 100)
        else:
            progress = 0

        leaderboard_data.append({
            'user': enroll.user,
            'progress': progress,
            'approved_count': approved_homeworks
        })

    # Progress bo'yicha saralash (Top 10)
    leaderboard_data = sorted(leaderboard_data, key=lambda x: x['progress'], reverse=True)[:10]

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'lessons': lessons,
        'leaderboard': leaderboard_data,
    }
    return render(request, 'courses/course_detail.html', context)


# ==========================================
# 3. KURSGA YOZILISH (SOTIB OLISH)
# ==========================================
@login_required(login_url='login')
def course_enroll(request, slug):
    course = get_object_or_404(Course, slug=slug)

    existing_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()

    if existing_enrollment:
        if existing_enrollment.status == 'active':
            messages.warning(request, "Siz bu kursga allaqachon a'zosiz!")
            return redirect('course_detail', slug=slug)
        elif existing_enrollment.status == 'pending':
            messages.info(request, "Sizning to'lovingiz tekshirilmoqda. Iltimos kuting.")
            return redirect('my_courses')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, request.FILES)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.user = request.user
            enrollment.course = course
            final_price = course.price

            code_str = form.cleaned_data.get('promocode')
            if code_str:
                try:
                    promo = PromoCode.objects.get(code=code_str, active=True, valid_to__gte=timezone.now())
                    if promo.allowed_courses.exists() and course not in promo.allowed_courses.all():
                        messages.error(request, "Bu promokod ushbu kursga amal qilmaydi.")
                        return render(request, 'courses/course_enroll.html', {'course': course, 'form': form})

                    discount_amount = (final_price * promo.discount_percentage) / 100
                    final_price -= discount_amount
                    enrollment.used_promocode = promo
                except PromoCode.DoesNotExist:
                    messages.error(request, "Promokod noto'g'ri yoki muddati tugagan.")
                    return render(request, 'courses/course_enroll.html', {'course': course, 'form': form})

            enrollment.final_price = final_price
            enrollment.save()
            messages.success(request, "To'lov cheki yuborildi! Admin tasdiqlashini kuting.")
            return redirect('my_courses')
    else:
        form = EnrollmentForm()

    context = {
        'course': course,
        'form': form,
        'card_number': "8600 0000 0000 0000"  # O'zingizni raqamingizni yozing
    }
    return render(request, 'courses/course_enroll.html', context)


# ==========================================
# 4. MENING KURSLARIM (MY LEARNINGS)
# ==========================================
@login_required(login_url='login')
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).order_by('-enrolled_at')
    for item in enrollments:
        first_lesson = item.course.lessons.order_by('order').first()
        item.first_lesson_slug = first_lesson.slug if first_lesson else None

    context = {
        'enrollments': enrollments
    }
    return render(request, 'courses/my_courses.html', context)


# ==========================================
# 5. DARS SAHIFASI (LESSON DETAIL)
# ==========================================
@login_required(login_url='login')
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)

    # 1. To'lov tekshiruvi
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course, status='active')

    # 2. Kirish huquqi (Qulf)
    if lesson.order > 1:
        prev_lesson = Lesson.objects.filter(course=course, order=lesson.order - 1).first()
        if prev_lesson:
            is_prev_approved = HomeworkSubmission.objects.filter(
                user=request.user, lesson=prev_lesson, is_approved=True
            ).exists()
            if not is_prev_approved:
                messages.error(request, "Oldingi dars vazifasi tasdiqlanmagan!")
                return redirect('course_detail', slug=course.slug)

    # 3. Sidebar darslari (Qulflar bilan)
    sidebar_lessons = list(course.lessons.all().order_by('order'))
    for item in sidebar_lessons:
        if item.order == 1:
            item.is_locked = False
        else:
            prev = course.lessons.filter(order=item.order - 1).first()
            if prev:
                is_ok = HomeworkSubmission.objects.filter(user=request.user, lesson=prev, is_approved=True).exists()
                item.is_locked = not is_ok
            else:
                item.is_locked = False

    # 4. Vazifa topshirish
    submission = HomeworkSubmission.objects.filter(user=request.user, lesson=lesson).first()
    if request.method == 'POST':
        form = HomeworkForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            new_sub = form.save(commit=False)
            new_sub.user = request.user
            new_sub.lesson = lesson
            new_sub.save()
            messages.success(request, "Vazifa yuborildi!")
            return redirect('lesson_detail', course_slug=course.slug, lesson_slug=lesson.slug)
    else:
        form = HomeworkForm(instance=submission)

    context = {
        'course': course,
        'lesson': lesson,
        'lessons': sidebar_lessons,
        'form': form,
        'submission': submission,
    }
    return render(request, 'courses/lesson_detail.html', context)