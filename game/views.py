import redis

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormMixin, BaseCreateView
from django.utils.translation import ugettext, ugettext_lazy as _
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.conf import settings

from .models import Game, Invite
from .forms import InviteForm, CreateMoveForm
from .utils import get_result
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
            u"""You have a new game invite from {0}
            <a href="{1}" class="btn btn-success invite_link"> Accept</a>
            <a href="{2}" class="btn btn-danger invite_link" id="decline"> Decline</a>"""
        ).format(self.request.user.username, accept_invite_url, decline_invite_url)
        strict_redis.publish('%d' % invite.invitee.pk, ['new_invite', redis_message])

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not form.is_valid():
            return HttpResponse(ugettext(u"Error occured."))
        self.form_valid(form)
        return HttpResponse(ugettext(u'Invite was successfully sent.'))


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


class CreateMoveView(RequirePostMixin, LoginRequiredMixin, BaseCreateView):

    form_class = CreateMoveForm

    def form_valid(self, form):
        move = form.save()
        game = form.cleaned_data['game']
        playfield = game.get_playfield()

        player = 'x' if game.first_user == self.request.user else 'o'
        opponent = playfield.get_opponent(player)

        opponent_user = game.first_user if player == 'o' else game.second_user

        if playfield.is_game_over():
            winner = playfield.get_winner()
            strict_redis.publish('%d' % self.request.user.pk,
                                 ['game_over', get_result(player, winner)])
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['opponent_moved', player, move.move])
            strict_redis.publish('%d' % opponent_user.pk,
                                 ['game_over', get_result(opponent, winner)])
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
            u"A new game has started <a href='{0}'>here.</a>"
        ).format(reverse('game_detail', args=[game.pk]))
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
