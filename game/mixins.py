from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class RequirePostMixin(object):

    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        return super(RequirePostMixin, self).dispatch(request, *args, **kwargs)
