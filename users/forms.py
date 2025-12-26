from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telegram_username = forms.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "telegram_username",
            "password1",
            "password2",
        )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "telegram_username",
            "avatar", # <--- YANGI
        )
