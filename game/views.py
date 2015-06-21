import redis
import random

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.conf import settings

from gevent.greenlet import Greenlet
from socketio.namespace import BaseNamespace
from socketio.sdjango import namespace

from users.models import User

from .models import Game, Move, Invite
from .forms import InviteForm


@namespace('/game')
class GameNamespace(BaseNamespace):
    def listener(self, chan):
        red = redis.StrictRedis(settings.REDIS_HOST)
        red = red.pubsub()
        red.subscribe(chan)

        print 'subscribed on chan ', chan

        while True:
            for i in red.listen():
                self.emit('message', i)

    def recv_message(self, message):
        action, pk = message.split(':')

        if action == 'subscribe':
            Greenlet.spawn(self.listener, pk)


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class UserListView(LoginRequiredMixin, FormMixin, ListView):

    template_name = 'user_list.html'
    queryset = User.objects.filter(logged_in=True)
    form_class = InviteForm

    def form_valid(self, invitee_pk, user):
        invitee = get_object_or_404(User, pk=invitee_pk)
        invite = Invite.objects.create(inviter=user, invitee=invitee)

        url = reverse('accept_invite', args=[invite.pk])
        messages.add_message(self.request, messages.SUCCESS, _(u'Invite was successfully sent'))

        red = redis.StrictRedis(settings.REDIS_HOST)
        red.publish('%d' % invite.invitee.id, ['new_invite', str(user.username), str(url)])

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        self.form_valid(form.cleaned_data['invitee_pk'], request.user)
        return super(UserListView, self).get(request, *args, **kwargs)


class GameDetailView(LoginRequiredMixin, DetailView):

    model = Game

    def get_context_data(self, **kwargs):
        context = super(GameDetailView, self).get_context_data(**kwargs)
        self.player = 'x' if self.object.first_user == self.request.user else 'o'
        self.playfield = self.object.get_playfield()
        status, notification_text = self.get_notification()
        context.update({
            'playfield': self.playfield,
            'player': self.player,
            'notification_text': notification_text,
            'status': status
        })
        return context

    def get_notification(self):
        if self.playfield.is_game_over():
            return self.get_result()
        else:
            return self.get_current_move()

    def get_current_move(self):
        if self.player == 'x':
            return 'warning', _(u'Your turn.')
        else:
            return 'warning', _(u'Your opponents turn.')

    def get_result(self):
        winner = self.playfield.get_winner()
        if winner and winner == self.player:
            return 'success', _(u'You won!')
        elif winner and winner != self.player:
            return 'danger', _(u'You lost the game.')
        else:
            return 'info', _(u'Its a tie!')


@login_required
def create_move(request, pk):
    game = _get_game(request.user, pk)
    if request.POST:
        move = int(request.POST['move'])
        red = redis.StrictRedis(settings.REDIS_HOST)

        # get player of move
        tic_player = 'x' if game.first_user == request.user else 'o'

        Move(game=game, user=request.user, move=move).save()
        playfield = game.get_playfield()
        playfield.make_move(move, tic_player)

        # get opponent
        opponent_user = game.first_user if tic_player == 'o' else game.second_user

        # # get computer
        # computer_user = _get_computer()
        # playing_computer = computer_user in [game.player1, game.player2]

        winner = playfield.get_winner()

        if playfield.is_game_over():
            red.publish('%d' % request.user.id, ['game_over', game.pk, winner])
            red.publish('%d' % opponent_user.id, ['opponent_moved', game.pk, tic_player, move])
            red.publish('%d' % opponent_user.id, ['game_over', game.pk, winner])
        else:
            red.publish('%d' % opponent_user.id, ['opponent_moved', game.pk, tic_player, move])

    return HttpResponse()


def _get_game(user, game_pk):
    game = get_object_or_404(Game, pk=game_pk)
    if not game.first_user == user and not game.second_user == user:
        raise Http404
    return game


@login_required
def accept_invite(request, invite_pk):
    invite = get_object_or_404(Invite, pk=invite_pk, is_active=True)

    if request.user == invite.invitee:
        coin_toss = random.choice([0, 1])

        if coin_toss == 0:
            game = Game(first_user=invite.inviter, second_user=request.user)
        else:
            game = Game(first_user=request.user, second_user=invite.inviter)

        game.save()

        red = redis.StrictRedis(settings.REDIS_HOST)
        red.publish('%d' % invite.inviter.id, ['game_started', game.id, str(request.user.username)])

        invite.delete()

        return redirect('game_detail', pk=game.pk)

    raise Http404
