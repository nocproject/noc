# ---------------------------------------------------------------------
# Django URL dispatcher.
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpResponseServerError

# NOC modules
from noc.core.debug import error_report

#
# Populated by `web` service
urlpatterns = []  # site.urls


def set_url_patterns(urls) -> None:
    global urlpatterns
    urlpatterns = urls


def handler500(request):
    error_report()
    return HttpResponseServerError("Internal Server Error")
