from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm


class RegisterFormView(SuccessMessageMixin, FormView):

    form_class = UserCreationForm
    template_name = "users/registration.html"
    success_message = _(u"User %(username)s was created successfully")

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('users_login')
