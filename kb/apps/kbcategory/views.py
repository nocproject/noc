# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KBCategory Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.kb.models import KBCategory
##
## KBCategory admin
##
class KBCategoryAdmin(admin.ModelAdmin):
    list_display=["name"]
##
## KBCategory application
##
class KBCategoryApplication(ModelApplication):
    model=KBCategory
    model_admin=KBCategoryAdmin
    menu="Setup | Categories"
