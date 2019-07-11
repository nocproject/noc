# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Django URL dispatcher.
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpResponseServerError

# NOC modules
from noc.lib.app.site import site
from noc.core.debug import error_report

#
# Discover all applications
#
site.autodiscover()
#
# Install URL handlers
#
urlpatterns = site.urls


def handler500(request):
    error_report()
    return HttpResponseServerError("Internal Server Error")
