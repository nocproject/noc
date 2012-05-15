# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Custom Field Enum Group
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.main.models import CustomFieldEnumGroup, CustomFieldEnumValue


class EnumGroupInline(admin.TabularInline):
    """
    Enum Group
    """
    model = CustomFieldEnumValue
    extra = 10


class EnumGroupAdmin(admin.ModelAdmin):
    inlines = [EnumGroupInline]
    list_display = ["name", "is_active", "description"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


class EnumGroupAdminApplication(ModelApplication):
    model = CustomFieldEnumGroup
    model_admin = EnumGroupAdmin
    menu = "Setup | Enum Groups"
