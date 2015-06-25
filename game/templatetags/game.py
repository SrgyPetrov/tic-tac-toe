from django.template import Library

from ..models import Invite

register = Library()


@register.inclusion_tag('game/tags/invitations.html', takes_context=True)
def invitations(context):
    request = context.get('request')
    return {
        'object_list': Invite.objects.filter(invitee=request.user)
    }
