from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from users.models import User


class UserListView(ListView):

    template_name = 'user_list.html'
    queryset = User.objects.filter(logged_in=True)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserListView, self).dispatch(*args, **kwargs)
