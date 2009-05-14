# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module MAIN
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.main.views import index,logout,report,report_index,success,failure,menu,search,config_index,config_view

urlpatterns = patterns ( None,
        (r"^$",        login_required(index)),
        (r"^logout/$", login_required(logout)),
        (r"^report/(?P<report>[a-z0-9\-_.]+)/$", login_required(report)),
        (r"^report/$", login_required(report_index)),
        (r"success/$", login_required(success)),
        (r"failure/$", login_required(failure)),
        (r"menu/$",    login_required(menu)),
        (r"search/$",  login_required(search)),
        (r"config/$",  login_required(config_index)),
        (r"config/(?P<config>.+)/$",  login_required(config_view)),
)
