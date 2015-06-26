import redis

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormMixin, BaseCreateView
from django.utils.translation import ugettext, ugettext_lazy as _
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings

from .models import Game, Invite
from .forms import InviteForm, CreateMoveForm
from .utils import get_result, get_players, change_game_status
from .mixins import LoginRequiredMixin, RequirePostMixin


strict_redis = redis.StrictRedis(settings.REDIS_HOST)


class UserListView(LoginRequiredMixin, FormMixin, TemplateView):

    template_name = 'game/game_user_list.html'
    form_class = InviteForm

    def form_valid(self, form):
        invite = form.save()
        accept_invite_url = reverse('accept_invite', args=[invite.pk])
        decline_invite_url = reverse('decline_invite', args=[invite.pk])
        redis_message = ugettext(
            u"""You have a new game invite from {0}. <br>
            <a href="{1}" class="btn btn-success invite-link"> Accept</a>
            <a href="{2}" class="btn btn-danger invite-link" id="decline"> Decline</a>"""
        ).format(self.request.user.username, accept_invite_url, decline_invite_url)
        strict_redis.publish('%d' % invite.invitee.pk, ['new_invite', redis_message])

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return JsonResponse(form.errors.as_json(), safe=False)
        self.form_valid(form)
        return HttpResponse(ugettext(u'Invite was successfully sent.'))


class GameDetailView(LoginRequiredMixin, DetailView):

    model = Game

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if not self.object.is_active:
            return redirect('game_user_list')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(GameDetailView, self).get_context_data(**kwargs)
        self.player = get_players(self.object, self.request.user)[0]
        self.playfield = self.object.get_playfield()
        notification_text, status = self.get_notification()
        context.update({
            'playfield': self.playfield,
            'player': self.player,
            'notification_text': notification_text,
            'status': status,
            'current_player': self.get_current_player()
        })
        return context

    def get_current_player(self):
        moves = self.object.move_set.all().order_by('-id')
        if moves:
            return 'o' if moves[0].user == self.object.first_user else 'x'
        return 'x'

    def get_notification(self):
        if self.playfield.is_game_over():
            winner = self.playfield.get_winner()
            return get_result(self.player, winner)
        return self.get_current_move_text()

    def get_current_move_text(self):
        if self.player == 'x':
            return _(u'Your turn.'), 'warning'
        return _(u'Your opponents turn.'), 'warning'


class CreateMoveView(RequirePostMixin, LoginRequiredMixin, BaseCreateView):

    form_class = CreateMoveForm

    def form_valid(self, form):
        move = form.save()
        game = form.cleaned_data['game']
        playfield = game.get_playfield()

        opponent_user = game.get_opponent_user(self.request.user)
        player, opponent = get_players(game, self.request.user)

        if playfield.is_game_over():
            winner = playfield.get_winner()
            strict_redis.publish('%d' % self.request.user.pk,
                                 ['game_over', get_result(player, winner)])
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['opponent_moved', player, move.move])
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['game_over', get_result(opponent, winner)])
            change_game_status(game, self.request.user)
            return HttpResponse()

        else:
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['opponent_moved', player, move.move, ugettext(u"Your turn.")])
        return HttpResponse(ugettext(u"Your opponents turn."))

    def form_invalid(self, form):
        return HttpResponse(ugettext(u"Error occured."))


@login_required
def accept_invite(request, invite_pk):
    invite = get_object_or_404(Invite, pk=invite_pk)

    if request.user == invite.invitee:
        game = Game.objects.create(first_user=invite.inviter, second_user=request.user)

        redis_message = ugettext(
            u"A new game with {0} has started <a href='{1}'>here.</a>"
        ).format(request.user, reverse('game_detail', args=[game.pk]))
        strict_redis.publish('%d' % invite.inviter.pk, ['game_started', redis_message])

        invite.delete()

        return redirect('game_detail', pk=game.pk)
    raise Http404


@login_required
def decline_invite(request, invite_pk):
    invite = get_object_or_404(Invite, pk=invite_pk)

    if request.user == invite.invitee:
        redis_message = ugettext(u"{0} has declined your invitation.").format(invite.invitee)
        strict_redis.publish('%d' % invite.inviter.pk, ['invitation_declined', redis_message])

        invite.delete()

        return HttpResponse(ugettext(u"Invitation declined."))
    raise Http404


@login_required
def replay_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    opponent = change_game_status(game, request.user)[1]
    opponent_user = game.get_opponent_user(request.user)

    redis_message = ugettext(
        u"{0} started game again. <a href='{1}' class='btn btn-danger refuse-link'> Refuse</a>"
    ).format(request.user, reverse('game_refuse', args=[pk]))
    strict_redis.publish('%d' % opponent_user.pk, ['replay', redis_message,
                         ugettext(u"Your turn."), opponent])
    return HttpResponse(ugettext(u"Your opponents turn."))


@login_required
def refuse_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    change_game_status(game, request.user)
    opponent_user = game.get_opponent_user(request.user)

    redis_message = ugettext(u"{0} has refused game.").format(request.user)
    strict_redis.publish('%d' % opponent_user.pk, ['refuse', redis_message, pk])

    if request.method == 'POST':
        return HttpResponse(ugettext(u"Game finished."))
    return redirect('game_user_list')
