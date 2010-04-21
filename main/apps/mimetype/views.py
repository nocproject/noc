# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIMEType Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import MIMEType
##
## MIMEType admin
##
class MIMETypeAdmin(admin.ModelAdmin):
    list_display=["extension","mime_type"]
    search_fields=["extension","mime_type"]
##
## MIMEType application
##
class MIMETypeApplication(ModelApplication):
    model=MIMEType
    model_admin=MIMETypeAdmin
    menu="Setup | MIME Types"
