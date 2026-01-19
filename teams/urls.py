# teams/urls.py
from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.TeamListView.as_view(), name='list'),
    path('create/', views.TeamCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TeamUpdateView.as_view(), name='edit'),
    path('<int:pk>/join/', views.TeamJoinView, name='join'),
    path('<int:pk>/leave/', views.TeamLeaveView, name='leave'),
    path('invite/<int:invitation_id>/accept/', views.InvitationAcceptView, name='accept_invitation'),
    path('invite/<int:invitation_id>/decline/', views.InvitationDeclineView, name='decline_invitation'),
    
    # URL для чата
    path('<int:pk>/chat/', views.team_chat, name='chat'),
    path('api/messages/<int:team_id>/', views.get_messages, name='get_messages'),
    path('api/send/', views.send_message, name='send_message'),
]