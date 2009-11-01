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
    (r"^view/chart/(?P<chart_id>\d+)/$", login_required(view_chart)),
    (r"^data/chart/(?P<chart_id>\d+)/$", login_required(chart_data)),
    (r"^view/ts/(?P<ts_id>\d+)/$",       login_required(view_ts)),
    (r"^data/ts/(?P<ts_id>\d+)/$",       login_required(ts_data)),
)
