from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Python, Django, JavaScript...'}),
        help_text="Перечислите ваши навыки через запятую",
        required=False
    )
    about = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о себе...'}),
        required=False
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "skills", "about", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.skills = self.cleaned_data["skills"]
        user.about = self.cleaned_data["about"]
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'github_link', 'telegram_link', 'phone']
        widgets = {
            'github_link': forms.URLInput(attrs={'placeholder': 'https://github.com/username'}),
            'telegram_link': forms.URLInput(attrs={'placeholder': 'https://t.me/username'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
        }
