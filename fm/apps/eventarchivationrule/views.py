# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventArchivationRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import EventArchivationRule
##
## EventArchivationRule admin
##
class EventArchivationRuleAdmin(admin.ModelAdmin):
    list_display=["event_class","ttl","ttl_measure","action"]
    list_filter=["action","event_class"]
##
## EventArchivationRule application
##
class EventArchivationRuleApplication(ModelApplication):
    model=EventArchivationRule
    model_admin=EventArchivationRuleAdmin
    menu="Setup | Archivation Rules"
