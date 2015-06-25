from django import forms

from .models import Move, Invite


class InviteForm(forms.ModelForm):

    class Meta:
        model = Invite
        fields = ['invitee', 'inviter']


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
