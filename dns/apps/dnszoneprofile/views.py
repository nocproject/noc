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
## List of master servers
##
def masters(obj):
    return u", ".join([s.name for s in obj.masters.all()])
masters.short_description = "Masters"

##
## List of slave servers
##
def slaves(obj):
    return u", ".join([s.name for s in obj.slaves.all()])
slaves.short_description = "Slaves"

##
## DNSZoneProfile admin
##
class DNSZoneProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "zone_ttl", "notification_group", masters, slaves]
    filter_horizontal=["masters", "slaves"]
##
## DNSZoneProfile application
##
class DNSZoneProfileApplication(ModelApplication):
    model=DNSZoneProfile
    model_admin=DNSZoneProfileAdmin
    menu="Setup | Zone Profiles"
