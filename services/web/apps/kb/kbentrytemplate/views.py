# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# KBEntryTemplate Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from django.contrib import admin
from noc.kb.models.kbentrytemplate import KBEntryTemplate
from noc.lib.app.modelapplication import ModelApplication


#
# KBEntryTemplate admin
#
class KBEntryTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "subject"]


#
# KBEntryTemplate application
#
class KBEntryTemplateApplication(ModelApplication):
    model = KBEntryTemplate
    model_admin = KBEntryTemplateAdmin
    menu = "Setup | Templates"
