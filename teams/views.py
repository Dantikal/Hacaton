from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Team, TeamInvitation, Message
from .forms import TeamCreateForm, TeamUpdateForm

class TeamListView(ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        return Team.objects.filter(is_active=True).select_related('leader')

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamCreateForm
    template_name = 'teams/team_create.html'
    success_url = reverse_lazy('teams:list')
    
    def form_valid(self, form):
        form.instance.leader = self.request.user
        response = super().form_valid(form)
        self.request.user.team = self.object
        self.request.user.save()
        return response

class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member'] = self.request.user.team == self.object
        context['is_leader'] = self.object.leader == self.request.user
        context['pending_invitations'] = TeamInvitation.objects.filter(
            team=self.object, 
            is_accepted=None
        )
        return context

class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamUpdateForm
    template_name = 'teams/team_edit.html'
    success_url = reverse_lazy('teams:list')
    
    def dispatch(self, request, *args, **kwargs):
        team = self.get_object()
        if team.leader != request.user:
            messages.error(request, 'Только лидер команды может редактировать информацию')
            return redirect('teams:detail', pk=team.pk)
        return super().dispatch(request, *args, **kwargs)

@login_required
def TeamJoinView(request, pk):
    team = get_object_or_404(Team, pk=pk)
    
    if request.user.team:
        messages.error(request, 'Вы уже состоите в команде')
        return redirect('teams:detail', pk=team.pk)
    
    if team.is_full():
        messages.error(request, 'Команда уже заполнена')
        return redirect('teams:detail', pk=team.pk)
    
    invitation, created = TeamInvitation.objects.get_or_create(
        team=team,
        invited_user=request.user,
        invited_by=team.leader,
        defaults={'message': f'Пользователь {request.user.username} хочет присоединиться к команде'}
    )
    
    if created:
        messages.success(request, 'Запрос на присоединение отправлен лидеру команды')
    else:
        messages.info(request, 'Вы уже отправляли запрос на присоединение')
    
    return redirect('teams:detail', pk=team.pk)

@login_required
def TeamLeaveView(request, pk):
    team = get_object_or_404(Team, pk=pk)
    
    if request.user.team != team:
        messages.error(request, 'Вы не состоите в этой команде')
        return redirect('teams:detail', pk=team.pk)
    
    if team.leader == request.user:
        messages.error(request, 'Лидер команды не может покинуть команду. Сначала передайте лидерство.')
        return redirect('teams:detail', pk=team.pk)
    
    request.user.team = None
    request.user.save()
    messages.success(request, 'Вы покинули команду')
    return redirect('teams:list')

@login_required
def InvitationAcceptView(request, invitation_id):
    invitation = get_object_or_404(TeamInvitation, pk=invitation_id)
    
    if invitation.team.leader != request.user:
        messages.error(request, 'Только лидер команды может принимать приглашения')
        return redirect('teams:detail', pk=invitation.team.pk)
    
    if invitation.is_accepted is not None:
        messages.error(request, 'Приглашение уже обработано')
        return redirect('teams:detail', pk=invitation.team.pk)
    
    if invitation.team.is_full():
        messages.error(request, 'Команда уже заполнена')
        return redirect('teams:detail', pk=invitation.team.pk)
    
    with transaction.atomic():
        invitation.is_accepted = True
        invitation.save()
        invitation.invited_user.team = invitation.team
        invitation.invited_user.save()
    
    messages.success(request, f'{invitation.invited_user.username} присоединился к команде')
    return redirect('teams:detail', pk=invitation.team.pk)

@login_required
def InvitationDeclineView(request, invitation_id):
    invitation = get_object_or_404(TeamInvitation, pk=invitation_id)
    
    if invitation.team.leader != request.user:
        messages.error(request, 'Только лидер команды может отклонять приглашения')
        return redirect('teams:detail', pk=invitation.team.pk)
    
    invitation.is_accepted = False
    invitation.save()
    messages.success(request, f'Приглашение для {invitation.invited_user.username} отклонено')
    return redirect('teams:detail', pk=invitation.team.pk)

@login_required
@require_GET
def get_messages(request, team_id):
    """API для получения сообщений чата"""
    try:
        team = get_object_or_404(Team, pk=team_id)
        
        # Проверяем, что пользователь состоит в команде
        if request.user.team != team:
            return JsonResponse({'error': 'Вы не состоите в этой команде'}, status=403)
        
        # Пытаемся получить сообщения
        try:
            messages_list = Message.objects.filter(team=team).select_related('author').order_by('created_at')
            
            messages_data = []
            for msg in messages_list:
                messages_data.append({
                    'id': msg.id,
                    'author': msg.author.get_full_name() or msg.author.username,
                    'content': msg.content,
                    'created_at': msg.created_at.strftime("%H:%M"),
                    'is_own': msg.author == request.user,
                })
            
            print(f"DEBUG: Found {len(messages_data)} messages for team {team_id}")  # Для отладки
            return JsonResponse({'messages': messages_data})
            
        except Exception as e:
            # Если есть проблемы с базой
            print(f"DEBUG: Error getting messages: {e}")  # Для отладки
            return JsonResponse({'messages': [], 'debug': str(e)})
            
    except Exception as e:
        print(f"DEBUG: General error: {e}")  # Для отладки
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def team_chat(request, pk):
    """View для отображения чата команды"""
    team = get_object_or_404(Team, pk=pk)
    
    # Проверяем, что пользователь состоит в команде
    if request.user.team != team:
        messages.error(request, 'Вы не состоите в этой команде')
        return redirect('teams:detail', pk=team.pk)
    
    # Получаем сообщения для отображения в шаблоне
    try:
        chat_messages = Message.objects.filter(team=team).select_related('author').order_by('created_at')
    except Exception as e:
        # Если таблицы сообщений нет
        print(f"DEBUG: Error getting messages: {e}")
        chat_messages = []
    
    return render(request, 'teams/team_chat.html', {
        'team': team,
        'messages': chat_messages,
    })

@login_required
@require_POST
@csrf_exempt
def send_message(request):
    """API для отправки сообщения"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        team_id = data.get('team_id')
        
        if not content:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        if not team_id:
            return JsonResponse({'error': 'Не указана команда'}, status=400)
        
        team = get_object_or_404(Team, pk=team_id)
        
        # Проверяем, что пользователь состоит в команде
        if request.user.team != team:
            return JsonResponse({'error': 'Вы не состоите в этой команде'}, status=403)
        
        # Создаем сообщение
        message = Message.objects.create(
            team=team,
            author=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'author': message.author.get_full_name() or message.author.username,
                'content': message.content,
                'created_at': message.created_at.strftime("%H:%M"),
                'is_own': True,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)