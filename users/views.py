from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ContactMessage

# Kurslar va Vazifalarni chaqiramiz
from courses.models import Enrollment, HomeworkSubmission

from .forms import SignupForm, ProfileEditForm


# ======================
# AUTH – SIGNUP
# ======================
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignupForm()

    return render(request, "users/signup.html", {"form": form})


# ======================
# AUTH – LOGIN
# ======================
class CustomLoginView(LoginView):
    template_name = "users/login.html"


# ======================
# PUBLIC PAGES
# ======================
def about(request):
    return render(request, "users/about.html")


def courses(request):
    return render(request, "users/courses.html")


# ======================
# AUTHENTICATED PAGES
# ======================

@login_required
def dashboard(request):
    user = request.user

    # 1. Statistika
    active_count = Enrollment.objects.filter(user=user, status='active').count()
    assignments_count = HomeworkSubmission.objects.filter(user=user).count()
    certificates_count = 0

    # 2. Jadval ma'lumotlari
    enrollments = Enrollment.objects.filter(user=user).order_by('-enrolled_at')

    course_data = []
    for item in enrollments:
        # Progressni hisoblash
        total_lessons = item.course.lessons.count()

        approved_homeworks = HomeworkSubmission.objects.filter(
            user=user,
            lesson__course=item.course,
            is_approved=True
        ).count()

        if total_lessons > 0:
            percent = int((approved_homeworks / total_lessons) * 100)
        else:
            percent = 0

        # --- MUAMMO SHU YERDA HAL QILINDI ---
        # Teskari bog'lanish nomini qidirib o'tirmaymiz, to'g'ridan-to'g'ri sanaymiz:
        students_count = Enrollment.objects.filter(course=item.course).count()
        # ------------------------------------

        course_data.append({
            'course': item.course,
            'status': item.status,
            'progress': percent,
            'total_students': students_count  # O'zgaruvchini beramiz
        })

    context = {
        'active_count': active_count,
        'assignments_count': assignments_count,
        'certificates_count': certificates_count,
        'course_data': course_data,
    }
    return render(request, "users/dashboard.html", context)


@login_required
def profile_view(request):
    return render(request, "users/profile.html")


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def my_learnings(request):
    return render(request, "users/my_learnings.html")


def blog_list(request):
    return render(request, "users/blog.html")


def blog_detail(request):
    return render(request, "users/blog_details.html")


def contact_page(request):
    if request.method == 'POST':
        # HTML formadagi inputlarning 'name' atributidan ma'lumotni olamiz
        f_name = request.POST.get('first_name', '')
        l_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        specialist = request.POST.get('specialist', '')
        date = request.POST.get('date', '')
        time = request.POST.get('time', '')

        # Ism va familiyani bitta 'name' maydoniga birlashtiramiz
        full_name = f"{f_name} {l_name}".strip()

        # Boshqa tafsilotlarni 'message' maydoniga yig'amiz
        full_message = f"Mutaxassis: {specialist}\nSana: {date}\nVaqt: {time}"

        # MUHIM: Bazada 'name' maydoni bo'sh bo'lmasligi shart (Constraint)
        if full_name and email:
            ContactMessage.objects.create(
                name=full_name,
                email=email,
                subject=f"Konsultatsiya: {specialist}",
                message=full_message
            )
            messages.success(request, "Xabaringiz muvaffaqiyatli yuborildi!")
            return redirect('contact_page')
        else:
            messages.error(request, "Iltimos, ism va emailingizni to'liq kiriting.")

    return render(request, 'users/contact.html')