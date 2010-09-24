# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ChangesQuarantineRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import ChangesQuarantineRule
##
## ChangesQuarantineRule admin
##
class ChangesQuarantineRuleAdmin(admin.ModelAdmin):
    list_display=["name","is_active","subject_re","action"]
    search_fields=["name","subject_re"]
    list_filter=["is_active","action"]
##
## ChangesQuarantineRule application
##
class ChangesQuarantineRuleApplication(ModelApplication):
    model=ChangesQuarantineRule
    model_admin=ChangesQuarantineRuleAdmin
    menu="Setup | Quarantine Rules"
