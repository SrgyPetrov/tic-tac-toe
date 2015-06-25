from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import ugettext as _
from django import forms

from .models import Move, Invite


class InviteForm(forms.ModelForm):

    class Meta:
        model = Invite
        fields = ['invitee', 'inviter']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _(u"You have already invited this user to game."),
            }
        }


class CreateMoveForm(forms.ModelForm):

    class Meta:
        model = Move
        fields = ['game', 'user', 'move']

    def clean(self):
        cleaned_data = super(CreateMoveForm, self).clean()
        game = cleaned_data['game']
        user = cleaned_data['user']
        if not game.first_user == user and not game.second_user == user:
            raise forms.ValidationError()
        return cleaned_data
