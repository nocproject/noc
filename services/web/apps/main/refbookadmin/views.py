# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# RefBook Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
from django.contrib import admin
from noc.core.translation import ugettext as _
from noc.lib.app.modelapplication import ModelApplication
from noc.main.models.refbook import RefBook
from noc.main.models.refbookfield import RefBookField


class RefBookFieldAdmin(admin.TabularInline):
    """
    RefBook field inlines
    """
    extra = 3
    model = RefBookField


class RefBookAdmin(admin.ModelAdmin):
    """
    Admin for Ref Books
    """
    list_display = ["name", "is_builtin", "is_enabled"]
    search_fields = ["name"]
    list_filter = ["is_enabled", "is_builtin"]
    inlines = [RefBookFieldAdmin]


class RefBookApplication(ModelApplication):
    """
    RefBook application
    """
    model = RefBook
    model_admin = RefBookAdmin
    menu = _("Setup") + " | " + _("Reference Books")
