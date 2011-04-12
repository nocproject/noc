# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CommandSnippet Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.sa.models import CommandSnippet


##
## CommandSnippet admin
##
class CommandSnippetAdmin(admin.ModelAdmin):
    list_display = ["name", "selector"]


##
## CommandSnippet application
## @todo: test form
##
class CommandSnippetApplication(ModelApplication):
    model = CommandSnippet
    model_admin = CommandSnippetAdmin
    menu = "Setup | Command Snippets"
