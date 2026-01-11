from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import Team, TeamInvitation
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
