# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Django URL dispatcher.
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.site import site, patterns

#
# Discover all applications
#
site.autodiscover()
#
# Install URL handlers
#
=======
##----------------------------------------------------------------------
## Django URL dispatcher.
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.site import site, patterns
from noc.lib.solutions import init_solutions

## Initialize custom fields and solutuins
init_solutions()
##
## Discover all applications
##
site.autodiscover()
##
## Install URL handlers
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
urlpatterns = patterns("",
    (r"^jsi18n/$", "django.views.i18n.javascript_catalog",
        {"packages": "django.conf"})
) + site.urls
