from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from .models import ChatRoom, Message
from teams.models import Team

class ChatListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/chat_list.html'
    context_object_name = 'chat_rooms'
    
    def get_queryset(self):
        user = self.request.user
        if user.team:
            return ChatRoom.objects.filter(team=user.team).select_related('team')
        return ChatRoom.objects.none()

class TeamChatView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'chat/team_chat.html'
    context_object_name = 'messages'
    paginate_by = 50
    
    def dispatch(self, request, *args, **kwargs):
        team_id = kwargs.get('team_id')
        team = get_object_or_404(Team, id=team_id)
        
        if request.user.team != team:
            return render(request, 'chat/no_access.html')
        
        self.team = team
        self.chat_room, created = ChatRoom.objects.get_or_create(team=team)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Message.objects.filter(
            chat_room=self.chat_room
        ).select_related('author').order_by('created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.team
        context['chat_room'] = self.chat_room
        return context

@csrf_exempt
@login_required
def SendMessageView(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        team_id = data.get('team_id')
        
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
        
        team = get_object_or_404(Team, id=team_id)
        
        if request.user.team != team:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        chat_room, created = ChatRoom.objects.get_or_create(team=team)
        
        message = Message.objects.create(
            chat_room=chat_room,
            author=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'author': message.author.username,
                'created_at': message.created_at.strftime('%H:%M'),
                'is_edited': message.is_edited
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def GetMessagesView(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.user.team != team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    chat_room, created = ChatRoom.objects.get_or_create(team=team)
    
    messages = Message.objects.filter(
        chat_room=chat_room
    ).select_related('author').order_by('created_at')
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'author': msg.author.username,
        'created_at': msg.created_at.strftime('%H:%M'),
        'is_edited': msg.is_edited
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})
