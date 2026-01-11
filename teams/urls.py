from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.TeamListView.as_view(), name='list'),
    path('create/', views.TeamCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TeamUpdateView.as_view(), name='edit'),
    path('<int:pk>/join/', views.TeamJoinView.as_view(), name='join'),
    path('<int:pk>/leave/', views.TeamLeaveView.as_view(), name='leave'),
    path('invite/<int:invitation_id>/accept/', views.InvitationAcceptView.as_view(), name='accept_invitation'),
    path('invite/<int:invitation_id>/decline/', views.InvitationDeclineView.as_view(), name='decline_invitation'),
]
