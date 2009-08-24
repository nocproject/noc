# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module PM
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.pm.views import *

urlpatterns = patterns ( "",
    (r"^$",                   login_required(index)),
    (r"^view/(?P<chart_id>\d+)/$", login_required(view)),
    (r"^data/(?P<chart_id>\d+)/$", login_required(data)),
)
