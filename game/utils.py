from django.utils.translation import ugettext
from django.http import Http404


def get_result(player, winner):
    if winner and winner == player:
        return ugettext(u'You won!'), 'success'
    elif winner and winner != player:
        return ugettext(u'You lost the game.'), 'danger'
    else:
        return ugettext(u'Its a tie!'), 'info'


def get_players(game, user):
    if game.first_user == user:
        return 'x', 'o'
    else:
        return 'o', 'x'


def change_game_status(game, user):
    if not user == game.first_user and not user == game.second_user:
        raise Http404

    if game.is_active is True:
        game.is_active = False
        game.save()
    else:
        game.is_active = True
        game.save()
        game.move_set.all().delete()

    return get_players(game, user)
