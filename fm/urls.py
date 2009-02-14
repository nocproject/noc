# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher for module FM
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from noc.fm.views import index,event,reclassify,create_rule,event_list_css,view_rules,py_event_class,py_event_classification_rule

urlpatterns = patterns ( "",
    (r"^(?P<event_id>\d+)/reclassify/$", login_required(reclassify)),
    (r"^(?P<event_id>\d+)/create_rule/$", login_required(create_rule)),
    (r"^(?P<event_id>\d+)/$", login_required(event)),
    (r"^event_list_css/$",    login_required(event_list_css)),
    (r"^view_rules/$",        login_required(view_rules)),
    (r"^py_event_class/(?P<event_class_id>\d+)/$", login_required(py_event_class)),
    (r"^py_event_classification_rule/(?P<rule_id>\d+)/$", login_required(py_event_classification_rule)),
    (r"^$",                   login_required(index)),
)
