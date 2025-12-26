from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',) # Faqat matn so'raymiz, muallifni avtomatik olamiz
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Izohingizni shu yerga yozing...',
                'rows': 4
            }),
        }