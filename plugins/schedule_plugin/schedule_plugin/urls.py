"""schedule_plugin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
import sys
import inspect

from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
sys.path.insert(0, ppp)

from schedule_app import info_handler, register_handler, healthcheck_handler, task_handler, views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'info/', info_handler.handle),
    url(r'config/', views.config, name='config'),
    url(r'register/', register_handler.handle),
    url(r'healthcheck/', healthcheck_handler.handle),
    url(r'task/', task_handler.handle)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
