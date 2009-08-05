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
from noc.kb.views import index,index_bookmarks,index_latest,index_popular,index_all,view,attachment,bookmark,template_index,from_template,\
    index_categories,index_category

urlpatterns = patterns ( None,
        (r"^$",                login_required(index)),
        (r"^bookmarks/$",      login_required(index_bookmarks)),
        (r"^latest/$",         login_required(index_latest)),
        (r"^popular/$",        login_required(index_popular)),
        (r"^all/$",            login_required(index_all)),
        (r"^categories/$",     login_required(index_categories)),
        (r"^categories/(?P<category_id>\d+)/$",     login_required(index_category)),
        (r"^(?P<kb_id>\d+)/$", login_required(view)),
        (r"^(?P<kb_id>\d+)/attachment/(?P<name>.+)/$", login_required(attachment)),
        (r"^(?P<kb_id>\d+)/bookmark/(?P<action>set|unset)/$", login_required(bookmark)),
        (r"^template/$",       login_required(template_index)),
        (r"^template/(?P<template_id>\d+)/$", login_required(from_template)),
)
