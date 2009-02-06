# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module IP
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.ip.views import index,vrf_index,allocate_block,deallocate_block,assign_address,revoke_address

urlpatterns = patterns ( "",
    (r"^$",                   login_required(index)),
    (r"^(?P<vrf_id>\d+)/$",   login_required(vrf_index)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/$",   login_required(vrf_index)),
    (r"^(?P<vrf_id>\d+)/allocate_block/$", login_required(allocate_block)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/allocate_block/$",   login_required(allocate_block)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/deallocate_block/$", login_required(deallocate_block)),
    (r"^(?P<vrf_id>\d+)/assign_address/$", login_required(assign_address)),
    (r"^(?P<vrf_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/assign_address/$", login_required(assign_address)),
    (r"^(?P<vrf_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/revoke_address/$", login_required(revoke_address)),
    
)
