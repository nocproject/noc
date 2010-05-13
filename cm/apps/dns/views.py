# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNS Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.cm.models import DNS
from noc.cm.repoapp import RepoApplication
##
## DNS admin
##
class DNSAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","status"]
    search_fields=["repo_path"]
##
## DNS application
##
class DNSApplication(RepoApplication):
    repo="dns"
    model=DNS
    model_admin=DNSAdmin
    menu="DNS Objects"
