from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('news/', views.NewsListView.as_view(), name='list'),
    path('news/create/', views.NewsCreateView.as_view(), name='create'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='edit'),
    path('schedule/', views.ScheduleListView.as_view(), name='schedule'),
    path('schedule/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('tasks/', views.TaskListView.as_view(), name='tasks'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
]
