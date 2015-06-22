from django.utils.translation import ugettext
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import Game


def get_result(player, winner):
    if winner and winner == player:
        return ugettext(u'You won!'), 'success'
    elif winner and winner != player:
        return ugettext(u'You lost the game.'), 'danger'
    else:
        return ugettext(u'Its a tie!'), 'info'


def get_game(user, game_pk):
    game = get_object_or_404(Game, pk=game_pk)
    if not game.first_user == user and not game.second_user == user:
        raise Http404
    return game
