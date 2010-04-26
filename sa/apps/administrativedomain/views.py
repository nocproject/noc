# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AdministrativeDomain Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.sa.models import AdministrativeDomain
##
## AdministrativeDomain admin
##
class AdministrativeDomainAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    search_fields=["name","description"]
##
## AdministrativeDomain application
##
class AdministrativeDomainApplication(ModelApplication):
    model=AdministrativeDomain
    model_admin=AdministrativeDomainAdmin
    menu="Setup | Administrative Domains"
