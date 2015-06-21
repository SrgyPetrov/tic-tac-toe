import socketio.sdjango

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^socket\.io', include(socketio.sdjango.urls)),
] + staticfiles_urlpatterns()

urlpatterns += i18n_patterns(
    url(r'', include('game.urls')),
    url(r'^users/', include('users.urls')),
)
