from django import forms
from .models import Enrollment, HomeworkSubmission

# ==========================================
# 1. TO'LOV VA CHEK YUKLASH FORMASI
# ==========================================
class EnrollmentForm(forms.ModelForm):
    # Promokod modelda yo'q, shuning uchun alohida maydon
    promocode = forms.CharField(
        required=False,
        label="Promokod (Agar bo'lsa)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masalan: NAVRUZ20'})
    )

    class Meta:
        model = Enrollment
        fields = ['payment_receipt'] # Faqat chek rasmini so'raymiz
        widgets = {
            'payment_receipt': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
        labels = {
            'payment_receipt': "To'lov chekini yuklang (Skrinshot)"
        }

# ==========================================
# 2. UYGA VAZIFA TOPSHIRISH FORMASI (YANGI)
# ==========================================
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ['file', 'text_answer']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'text_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Javobingizni shu yerga yozing...'}),
        }
        labels = {
            'file': "Fayl yuklash (Rasm/PDF/Word)",
            'text_answer': "Yozma javob"
        }