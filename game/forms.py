from django.utils.translation import ugettext as _
from django import forms

from .models import Move, Invite


class InviteForm(forms.ModelForm):

    class Meta:
        model = Invite
        fields = ['invitee', 'inviter']

    def clean(self):
        cleaned_data = super(InviteForm, self).clean()
        invitee = cleaned_data.get('invitee')
        inviter = cleaned_data.get('inviter')

        if Invite.objects.filter(invitee=invitee, inviter=inviter).exists():
            raise forms.ValidationError(_(u"You have already invited this user to game."))

        if Invite.objects.filter(invitee=inviter, inviter=invitee).exists():
            raise forms.ValidationError(
                _(u"%s has already invited you to the game.") % invitee.username
            )

        return cleaned_data


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
