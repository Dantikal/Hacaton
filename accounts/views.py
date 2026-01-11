from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile
from .forms import CustomUserCreationForm, ProfileForm

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('news:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        Profile.objects.create(user=self.object)
        return response

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile
