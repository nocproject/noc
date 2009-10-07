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
from noc.ip.views import index,vrf_index,allocate_block,deallocate_block,assign_address,revoke_address,block_tools,download_ips,\
    upload_ips,upload_axfr,bind_vc

urlpatterns = patterns ( "",
    (r"^$",                   login_required(index)),
    (r"^(?P<vrf_id>\d+)/$",   login_required(vrf_index)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/$",   login_required(vrf_index)),
    (r"^(?P<vrf_id>\d+)/allocate_block/$", login_required(allocate_block)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/allocate_block/$",   login_required(allocate_block)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/deallocate_block/$", login_required(deallocate_block)),
    (r"^(?P<vrf_id>\d+)/assign_address/$", login_required(assign_address)),
    (r"^(?P<vrf_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/assign_address/$", login_required(assign_address)),
    (r"^(?P<vrf_id>\d+)/(?P<new_ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/assign_address/new/$", login_required(assign_address)),
    (r"^(?P<vrf_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3})/revoke_address/$", login_required(revoke_address)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/tools/$", login_required(block_tools)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/download_ips/$", login_required(download_ips)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/upload_ips/$", login_required(upload_ips)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/upload_axfr/$", login_required(upload_axfr)),
    (r"^(?P<vrf_id>\d+)/(?P<prefix>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}/\d{1,2})/vc/bind/$",     login_required(bind_vc)),
)
