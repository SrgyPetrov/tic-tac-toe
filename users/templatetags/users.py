import re

from django.template import Library

register = Library()


@register.inclusion_tag('users/tags/switch_language_panel.html', takes_context=True)
def switch_language_panel(context):
    request = context['request']
    base_url = re.sub(r'^/[^/]*', '', request.path)
    return {'base_url': base_url}
