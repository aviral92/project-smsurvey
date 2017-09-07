import os
import inspect
import sys

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
sys.path.insert(0, ppp)

from plugins.rapidsms_plugin.responsehandler import poke_handler, message_handler, info_handler, register_handler, views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # RapidSMS core URLs
    url(r'^accounts/', include('rapidsms.urls.login_logout')),
    url(r'^$', 'rapidsms.views.dashboard', name='rapidsms-dashboard'),
    # RapidSMS contrib app URLs
    url(r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    url(r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    url(r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    url(r'^registration/', include('rapidsms.contrib.registration.urls')),
    # Twilio backend
    url(r'^backend/twilio/', include('rtwilio.urls')),
    # Third party URLs
    url(r'^selectable/', include('selectable.urls')),
    # Interface implementation
    url(r'poke/', poke_handler.handle),
    url(r'message/', message_handler.handle),
    url(r'info/', info_handler.handle),
    url(r'register/', register_handler.handle),
    url(r'config/', views.config, name='config')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
