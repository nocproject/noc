# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RefBook Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import RefBook,RefBookField
##
## RefBook field inlines
##
class RefBookFieldAdmin(admin.TabularInline):
    extra=3
    model=RefBookField
##
## Admin for Ref Books
##
class RefBookAdmin(admin.ModelAdmin):
    list_display=["name","is_builtin","is_enabled"]
    search_fields=["name"]
    list_filter=["is_enabled","is_builtin"]
    inlines=[RefBookFieldAdmin]
##
## RefBook application
##
class RefBookApplication(ModelApplication):
    model=RefBook
    model_admin=RefBookAdmin
    menu="Setup | Reference Books"
