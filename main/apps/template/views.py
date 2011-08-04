# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Template Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.main.models import Template


class TemplateAdmin(admin.ModelAdmin):
    """
    Template admin
    """
    list_display = ["name", "subject"]
    search_fields = ["name", "subject", "body"]


class TemplateApplication(ModelApplication):
    """
    Template application
    """
    model = Template
    model_admin = TemplateAdmin
    menu = "Setup | Templates"
