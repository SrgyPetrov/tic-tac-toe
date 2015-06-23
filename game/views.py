import redis

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.conf import settings

from .models import Game, Move, Invite
from .forms import InviteForm
from .utils import get_result, get_game


strict_redis = redis.StrictRedis(settings.REDIS_HOST)


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class UserListView(LoginRequiredMixin, FormMixin, TemplateView):

    template_name = 'game/game_user_list.html'
    form_class = InviteForm

    def form_valid(self, invitee_pk):
        invite_url = self.create_invite(invitee_pk)
        messages.add_message(self.request, messages.SUCCESS, _(u'Invite was successfully sent'))
        redis_message = ugettext(
            u'You have a new game invite from {0} <a href="{1}"> Accept?</a>'
        ).format(self.request.user.username, invite_url)
        strict_redis.publish('%d' % invitee_pk, ['new_invite', redis_message])

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        self.form_valid(form.cleaned_data['invitee_pk'])
        return super(UserListView, self).get(request, *args, **kwargs)

    def create_invite(self, invitee_pk):
        invitee = get_object_or_404(User, pk=invitee_pk)
        invite = Invite.objects.create(inviter=self.request.user, invitee=invitee)
        return reverse('accept_invite', args=[invite.pk])


class GameDetailView(LoginRequiredMixin, DetailView):

    model = Game

    def get_context_data(self, **kwargs):
        context = super(GameDetailView, self).get_context_data(**kwargs)
        self.player = 'x' if self.object.first_user == self.request.user else 'o'
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


@login_required
def create_move(request, pk):
    game = get_game(request.user, pk)
    if request.POST:
        move = int(request.POST['move'])
        Move.objects.create(game=game, user=request.user, move=move)

        playfield = game.get_playfield()

        player = 'x' if game.first_user == request.user else 'o'
        opponent = playfield.get_opponent(player)

        opponent_user = game.first_user if player == 'o' else game.second_user

        if playfield.is_game_over():
            winner = playfield.get_winner()
            strict_redis.publish('%d' % request.user.pk,
                                 ['game_over', get_result(player, winner)])
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['opponent_moved', player, move])
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['game_over', get_result(opponent, winner)])
            return HttpResponse()

        else:
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['opponent_moved', player, move, ugettext(u"Your turn.")])
    return HttpResponse(ugettext(u"Your opponents turn."))


@login_required
def accept_invite(request, invite_pk):
    invite = get_object_or_404(Invite, pk=invite_pk, is_active=True)

    if request.user == invite.invitee:
        game = Game.objects.create(first_user=invite.inviter, second_user=request.user)

        redis_message = ugettext(
            u"A new game has started <a href='{0}'>here.</a>"
        ).format(reverse('game_detail', args=[game.pk]))

        strict_redis.publish('%d' % invite.inviter.pk, ['game_started', redis_message])

        invite.delete()

        return redirect('game_detail', pk=game.pk)

    raise Http404
