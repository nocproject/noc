# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSServer Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.dns.models import DNSServer
##
## DNSServer admin
##
class DNSServerAdmin(admin.ModelAdmin):
    list_display=["name","generator_name","ip","location","description"]
    search_fields=["name","description","ip"]
    list_filter=["generator_name"]
##
## DNSServer application
##
class DNSServerApplication(ModelApplication):
    model=DNSServer
    model_admin=DNSServerAdmin
    menu="Setup | DNS Servers"
