# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module CM
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.cm.views import view,diff

urlpatterns = patterns ( "",
    (r"^view/(?P<repo>[^/]+)/(?P<object_id>\d+)/$", login_required(view)),
    (r"^view/(?P<repo>[^/]+)/(?P<object_id>\d+)/(?P<revision>\d+)/$", login_required(view)),
    (r"^view/(?P<repo>[^/]+)/(?P<object_id>\d+)/text/$", login_required(view), {"format":"text"}),
    (r"^view/(?P<repo>[^/]+)/(?P<object_id>\d+)/(?P<revision>\d+)/text/$", login_required(view), {"format":"text"}),
    (r"^view/(?P<repo>[^/]+)/(?P<object_id>\d+)/diff/$", login_required(diff)),
    (r"^view/(?P<repo>[^/]+)/(?P<object_id>\d+)/diff/(?P<mode>[u2])/(?P<r1>.+)/(?P<r2>.+)/$", login_required(diff)),
)
