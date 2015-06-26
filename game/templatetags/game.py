from django.template import Library
from django.db.models import Q

from ..models import Invite, Game

register = Library()


@register.inclusion_tag('game/tags/invitations.html', takes_context=True)
def invitations(context):
    request = context.get('request')
    return {
        'object_list': Invite.objects.filter(invitee=request.user)
    }


@register.inclusion_tag('game/tags/active_games.html', takes_context=True)
def active_games(context):
    request = context.get('request')
    q = Q(first_user=request.user) | Q(second_user=request.user)
    return {
        'object_list': Game.objects.filter(q, is_active=True),
        'user': request.user
    }


@register.filter
def opponent(game, user):
    return game.get_opponent_user(user)
