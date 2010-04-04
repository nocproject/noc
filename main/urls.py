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
from noc.main.views import *
from django.contrib import databrowse
from noc.lib.decorators import superuser_required

urlpatterns = patterns ( None,
        (r"^$",        login_required(index)),
        (r"^logout/$", login_required(logout)),
        (r"^databrowse/(.*)", superuser_required(databrowse.site.root)),
        (r"^report/(?P<report>[a-z0-9\-_.]+)/$", login_required(report)),
        (r"^report/$", login_required(report_index)),
        (r"^calculator/(?P<calculator>[a-z0-9\-_.]+)/$", login_required(calculator)),
        (r"^calculator/$", login_required(calculator_index)),
        (r"^success/$", login_required(success)),
        (r"^failure/$", login_required(failure)),
        (r"^menu/$",    login_required(menu)),
        (r"^search/$",  login_required(search)),
        (r"^config/$",  login_required(config_index)),
        (r"^config/(?P<config>.+)/$",  login_required(config_view)),
        (r"^refbook/$", login_required(refbook_index)),
        (r"^refbook/(?P<refbook_id>\d+)/$",                            login_required(refbook_view)),
        (r"^refbook/(?P<refbook_id>\d+)/new/$",                        login_required(refbook_new)),
        (r"^refbook/(?P<refbook_id>\d+)/(?P<record_id>\d+)/$",         login_required(refbook_item)),
        (r"^refbook/(?P<refbook_id>\d+)/(?P<record_id>\d+)/edit/$",    login_required(refbook_edit)),
        (r"^refbook/(?P<refbook_id>\d+)/(?P<record_id>\d+)/delete/$",  login_required(refbook_delete)),
        (r"^time_pattern/test/(?P<time_patterns>\d+(?:,\d+)*)/$",      login_required(test_time_patterns)),
)
