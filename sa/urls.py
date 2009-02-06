# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module SA
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.sa.views import object_scripts,object_script

urlpatterns = patterns ( "",
    (r"^(?P<object_id>\d+)/scripts/$", login_required(object_scripts)),
    (r"^(?P<object_id>\d+)/scripts/(?P<script>[^/]+)/$", login_required(object_script)),
)
