from django.conf.urls import patterns, url

from .views import UserListView, GameDetailView, accept_invite, create_move


urlpatterns = patterns(
    '',
    url(r'^$', UserListView.as_view(), name='user_list'),
    url(r'^game/(?P<pk>\d+)/$', GameDetailView.as_view(), name='game_detail'),
    url(r'^invite/(?P<invite_pk>\d+)/$', accept_invite, name='accept_invite'),
    url(r'^game/(?P<pk>\d+)/create_move/$', create_move, name='game_create_move'),
)
