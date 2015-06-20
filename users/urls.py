from django.conf.urls import url, patterns
from django.contrib.auth.views import login, logout_then_login

from .views import RegisterFormView


urlpatterns = patterns(
    '',
    url(r'^login/$', login, name='users_login', kwargs={'template_name': 'users/login.html'}),
    url(r'^logout/$', logout_then_login, name='users_logout'),
    url(r'^registration/$', RegisterFormView.as_view(), name='users_registration')
)
