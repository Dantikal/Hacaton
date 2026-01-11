from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db import models
from .models import News, Schedule, Task
from .forms import NewsForm, ScheduleForm, TaskForm

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

class HomeView(ListView):
    model = News
    template_name = 'news/home.html'
    context_object_name = 'news_list'
    paginate_by = 5
    
    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем статистику
        from django.db.models import Count
        from teams.models import Team
        from accounts.models import User
        
        context['teams_count'] = Team.objects.filter(is_active=True).count()
        context['users_count'] = User.objects.filter(role='participant').count()
        context['news_count'] = News.objects.filter(is_published=True).count()
        
        return context

class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('author')

class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'

class NewsCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')
    
    def test_func(self):
        return self.request.user.role == 'admin'

class ScheduleListView(ListView):
    model = Schedule
    template_name = 'news/schedule.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        return Schedule.objects.all().order_by('start_time')

class ScheduleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'news/schedule_form.html'
    success_url = reverse_lazy('news:schedule')
    
    def test_func(self):
        return self.request.user.role == 'admin'

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'news/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()
        
        if user.role != 'admin':
            queryset = queryset.filter(
                models.Q(assigned_to=user) | 
                models.Q(team=user.team)
            ).distinct()
        
        return queryset.select_related('assigned_to', 'team')

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'news/task_detail.html'
    context_object_name = 'task'

class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'news/task_form.html'
    success_url = reverse_lazy('news:tasks')
    
    def test_func(self):
        return self.request.user.role == 'admin'

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'news/task_form.html'
    success_url = reverse_lazy('news:tasks')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        if user.role != 'admin':
            kwargs['user'] = user
        return kwargs

# Custom error handlers
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_500(request):
    return render(request, '500.html', status=500)
