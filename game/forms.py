from django import forms


class InviteForm(forms.Form):

    invitee_pk = forms.IntegerField(widget=forms.widgets.HiddenInput())
