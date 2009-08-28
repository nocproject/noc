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
from noc.sa.views import object_scripts,object_script,tools,upload_managed_objects,test_selector,mr_task,mr_task_result,run_now

urlpatterns = patterns ( "",
    (r"^(?P<object_id>\d+)/scripts/$",  login_required(object_scripts)),
    (r"^(?P<object_id>\d+)/scripts/(?P<script>[^/]+)/$", login_required(object_script)),
    (r"^tools/$",                       login_required(tools)),
    (r"^tools/upload_managed_objects/", login_required(upload_managed_objects)),
    (r"^test_selector/(?P<selector_id>\d+)", login_required(test_selector)),
    (r"^mr_task/$",                     login_required(mr_task)),
    (r"^mr_task/(?P<task_id>\d+)/$",    login_required(mr_task_result)),
    (r"^task/(?P<task_id>\d+)/now/",    login_required(run_now)),
)
