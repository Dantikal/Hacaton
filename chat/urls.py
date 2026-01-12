# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatListView.as_view(), name='list'),
    path('team/<int:team_id>/', views.TeamChatView.as_view(), name='team_chat'),
    
    # ИЗМЕНИТЬ: убрать .as_view() для функций
    path('api/send/', views.SendMessageView, name='send_message'),          # ← без .as_view()
    path('api/messages/<int:team_id>/', views.GetMessagesView, name='get_messages'),  # ← без .as_view()
]