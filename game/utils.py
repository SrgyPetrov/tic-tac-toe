from django.utils.translation import ugettext


def get_result(player, winner):
    if winner and winner == player:
        return ugettext(u'You won!'), 'success'
    elif winner and winner != player:
        return ugettext(u'You lost the game.'), 'danger'
    else:
        return ugettext(u'Its a tie!'), 'info'


def get_players(game, user):
    if game.first_user == user:
        return game.second_user, 'x', 'o'
    else:
        return game.first_user, 'o', 'x'
