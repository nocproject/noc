# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Django URL dispatcher.
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.conf.urls import url
from django.http import HttpResponseServerError
# NOC modules
from noc.lib.app.site import site, patterns
from noc.core.debug import error_report

#
# Discover all applications
#
site.autodiscover()
#
# Install URL handlers
#
urlpatterns = patterns(
    "",
    (url('jsi18n/', 'django.views.i18n.javascript_catalog', {"packages": "django.conf"}, name='javascript-catalog'))
) + site.urls


def handler500(request):
    error_report()
    return HttpResponseServerError("Internal Server Error")
