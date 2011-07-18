# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System Template Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.main.models import SystemTemplate


class SystemTemplateAdmin(admin.ModelAdmin):
    """
    System template admin
    """
    list_display = ["name", "template"]
    search_fields = ["name"]


class SystemTemplateApplication(ModelApplication):
    """
    SystemTemplate application
    """
    model = SystemTemplate
    model_admin = SystemTemplateAdmin
    menu = "Setup | System Templates"
