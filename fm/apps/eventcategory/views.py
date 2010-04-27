# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventCategory Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import EventCategory
##
## EventCategory admin
##
class EventCategoryAdmin(admin.ModelAdmin):
    pass
##
## EventCategory application
##
class EventCategoryApplication(ModelApplication):
    model=EventCategory
    model_admin=EventCategoryAdmin
    menu="Setup | Event Categories"
