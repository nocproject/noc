# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## {{module}}.{{app}} application
##----------------------------------------------------------------------
## Copyright (C) 2007-{{year}} The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.{{module}}.models import {{model}}


class {{model}}Admin(admin.ModelAdmin):
    """
    {{model}} admin
    """
    pass


class {{model}}Application(ModelApplication):
    """
    {{model}} application
    """
    model = {{model}}
    model_admin = {{model}}Admin
    menu = "Setup | {{model}}"
