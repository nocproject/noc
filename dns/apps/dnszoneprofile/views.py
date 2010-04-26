# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZoneProfile Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.dns.models import DNSZoneProfile
##
## DNSZoneProfile admin
##
class DNSZoneProfileAdmin(admin.ModelAdmin):
    filter_horizontal=["masters","slaves"]
##
## DNSZoneProfile application
##
class DNSZoneProfileApplication(ModelApplication):
    model=DNSZoneProfile
    model_admin=DNSZoneProfileAdmin
    menu="Setup | Zone Profiles"
