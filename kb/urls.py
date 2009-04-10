# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.kb.views import index,view

urlpatterns = patterns ( None,
        (r"^$",                login_required(index)),
        (r"^(?P<kb_id>\d+)/$", login_required(view)),
)
