from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('participant', 'Участник'),
        ('admin', 'Администратор'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    skills = models.TextField(blank=True, help_text="Навыки через запятую")
    about = models.TextField(blank=True, help_text="О себе")
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    github_link = models.URLField(blank=True)
    telegram_link = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
