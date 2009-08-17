# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module DNS
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.dns.views import zone,zone_rpsl,upload_zones,tools

urlpatterns = patterns ( "",
    (r"(?P<zone>[a-zA-Z0-9\-.]+)/zone/(?P<ns_id>\d+)/",         login_required(zone)),
    (r"(?P<zone>[a-zA-Z0-9\-.]+)/zone/rpsl/",                   login_required(zone_rpsl)),
    (r"^tools/$",                                               login_required(tools)),
    (r"^tools/upload_zones/$",                                  login_required(upload_zones)),
)
