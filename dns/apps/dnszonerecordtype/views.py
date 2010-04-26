# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZoneRecordType Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.dns.models import DNSZoneRecordType
##
## DNSZoneRecordType admin
##
class DNSZoneRecordTypeAdmin(admin.ModelAdmin):
    list_display=["type","is_visible","validation"]
    search_fields=["type"]
    list_filter=["is_visible"]
##
## DNSZoneRecordType application
##
class DNSZoneRecordTypeApplication(ModelApplication):
    model=DNSZoneRecordType
    model_admin=DNSZoneRecordTypeAdmin
    menu="Setup | Zone RR Types"
