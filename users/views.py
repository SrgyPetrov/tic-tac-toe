from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView
from django.core.urlresolvers import reverse

from .forms import RegistrationForm


class RegisterFormView(SuccessMessageMixin, FormView):

    form_class = RegistrationForm
    template_name = "users/registration.html"
    success_message = "%(username)s was created successfully"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('users_login')
