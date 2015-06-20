from django.conf.urls import patterns, url

from game.views import UserListView


urlpatterns = patterns(
    '',
    url(r'^$', UserListView.as_view(), name='user_list'),
)
