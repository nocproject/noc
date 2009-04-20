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
from noc.kb.views import index,index_latest,index_popular,index_all,view,attachment

urlpatterns = patterns ( None,
        (r"^$",                login_required(index)),
        (r"^latest/$",         login_required(index_latest)),
        (r"^popular/$",        login_required(index_popular)),
        (r"^all/$",            login_required(index_all)),
        (r"^(?P<kb_id>\d+)/$", login_required(view)),
        (r"^(?P<kb_id>\d+)/attachment/(?P<name>.+)/$", login_required(attachment)),
)
