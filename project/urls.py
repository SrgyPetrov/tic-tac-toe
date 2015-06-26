import socketio.sdjango

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include, url
from django.views.i18n import javascript_catalog

js_info_dict = {
    'packages': ('project',),
}

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^socket\.io', include(socketio.sdjango.urls)),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
] + staticfiles_urlpatterns()

urlpatterns += i18n_patterns(
    url(r'', include('game.urls')),
    url(r'^users/', include('users.urls')),
)
