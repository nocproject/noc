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
from noc.fm.views import index,event,reclassify_event,open_event,close_event,create_rule,event_list_css,view_rules,\
    py_event_class,py_event_classification_rule,upload_mib,lookup_managed_object,lookup_events,reload_classifier_config,\
    clone_rule,create_postprocessing_rule,clone_postprocessing_rule,py_event_correlation_rule,reload_correlator_config,\
    active_problems_summary

urlpatterns = patterns ( "",
    (r"^(?P<event_id>\d+)/status/reclassify/$", login_required(reclassify_event)),
    (r"^(?P<event_id>\d+)/status/open/$",       login_required(open_event)),
    (r"^(?P<event_id>\d+)/status/close/$",      login_required(close_event)),
    (r"^(?P<event_id>\d+)/create_rule/$", login_required(create_rule)),
    (r"^(?P<event_id>\d+)/create_postprocessing_rule/$", login_required(create_postprocessing_rule)),
    (r"^(?P<event_id>\d+)/$", login_required(event)),
    (r"^event_list_css/$",    login_required(event_list_css)),
    (r"^view_rules/$",        login_required(view_rules)),
    (r"^py_event_class/(?P<event_class_id>\d+)/$", login_required(py_event_class)),
    (r"^py_event_classification_rule/(?P<rule_id>\d+)/$", login_required(py_event_classification_rule)),
    (r"^py_event_correlation_rule/(?P<rule_id>\d+)/$", login_required(py_event_correlation_rule)),
    (r"^upload_mib/$",        login_required(upload_mib)),
    (r"^$",                   login_required(index)),
    (r"^lookup/managed_object/", lookup_managed_object),
    (r"^lookup/events/",      lookup_events),
    (r"^reload_classifier_config", login_required(reload_classifier_config)),
    (r"^reload_correlator_config", login_required(reload_correlator_config)),
    (r"^clone_rule/(?P<rule_id>\d+)/$", login_required(clone_rule)),
    (r"^clone_postprocessing_rule/(?P<rule_id>\d+)/$", login_required(clone_postprocessing_rule)),
    (r"^active_problems_summary/$", login_required(active_problems_summary)),
)
