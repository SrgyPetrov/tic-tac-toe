from django.utils.translation import ugettext


def get_result(player, winner):
    if winner and winner == player:
        return ugettext(u'You won!'), 'success'
    elif winner and winner != player:
        return ugettext(u'You lost the game.'), 'danger'
    else:
        return ugettext(u'Its a tie!'), 'info'
