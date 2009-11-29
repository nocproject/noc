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
from noc.peer.views import as_rpsl,as_set_rpsl,as_dot,lg,lg_json,inet_rtr_rpsl,person_rpsl,maintainer_rpsl,prefix_list_builder,as_rpsl_update

urlpatterns = patterns ( "",
    (r"^AS/(?P<asn>\d+)/rpsl/$",                   login_required(as_rpsl)),
    (r"^AS/(?P<asn>\d+)/rpsl/update/$",            login_required(as_rpsl_update)),
    (r"^AS/(?P<asn>\d+)/dot/$",                    login_required(as_dot)),
    (r"^AS-SET/(?P<as_set>AS-[A-Z0-9\-]+)/rpsl/$", login_required(as_set_rpsl)),
    (r"^INET-RTR/(?P<router>[A-Za-z0-9\-.]+)/rpsl/$", login_required(inet_rtr_rpsl)),
    (r"^person/(?P<person_id>\d+)/rpsl/$",         login_required(person_rpsl)),
    (r"^maintainer/(?P<mnt_id>\d+)/rpsl/$",        login_required(maintainer_rpsl)),
    (r"lg/(?P<task_id>\d+)/$",                    lg_json),
    (r"lg/",                                      lg),
    (r"builder/prefix_list/$",                    login_required(prefix_list_builder)),
)
