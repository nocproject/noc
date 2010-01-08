# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module PEER
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.peer.views import as_dot,lg,lg_json,prefix_list_builder

urlpatterns = patterns ( "",
    (r"^AS/(?P<asn>\d+)/dot/$",                    login_required(as_dot)),
    (r"lg/(?P<task_id>\d+)/$",                    lg_json),
    (r"lg/",                                      lg),
    (r"builder/prefix_list/$",                    login_required(prefix_list_builder)),
)
