# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module VC
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.vc.views import sa_import_vlans

urlpatterns = patterns ( None,
        (r"^sa_import_vlans/$",        login_required(sa_import_vlans)),
)
