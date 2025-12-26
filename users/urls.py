from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from . import views

urlpatterns = [
    # ======================
    # AUTHENTICATION (Ro'yxatdan o'tish va Kirish)
    # ======================
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),

    # ======================
    # DASHBOARD & PROFILE (Shaxsiy kabinet)
    # ======================
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # ======================
    # LEARNINGS (Kurslar va ta'lim)
    # ======================
    path("courses/", views.courses, name="courses"),
    path("my-learnings/", views.my_learnings, name="my_learnings"),

    # ======================
    # CONTACT (Aloqa sahifasi)
    # ======================
    path("contact/", views.contact_page, name="contact_page"),

    # ======================
    # PUBLIC PAGES (Ochiq sahifalar)
    # ======================
    path("about/", views.about, name="about"),

    # ======================
    # PASSWORD MANAGEMENT (Xavfsizlik)
    # ======================
    path(
        "password/change/",
        PasswordChangeView.as_view(
            template_name="users/password_change.html",
            success_url="/password/change/done/",
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html",
        ),
        name="password_change_done",
    ),
]