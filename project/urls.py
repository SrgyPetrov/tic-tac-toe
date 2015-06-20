from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', include('game.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
