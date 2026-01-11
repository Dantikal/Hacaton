from django import forms
from .models import Team

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'max_members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название команды'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите вашу команду, идеи, проект...'
            }),
            'max_members': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 10,
                'value': 4
            }),
        }

class TeamUpdateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'max_members', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'max_members': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 10
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
