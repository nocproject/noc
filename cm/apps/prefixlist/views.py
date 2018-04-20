# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PrefixList Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.cm.repoapp import RepoApplication
from noc.cm.models import PrefixList
##
## PrefixList admin
##
class PrefixListAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","status"]
    search_fields=["repo_path"]
##
## PrefixList application
##
class PrefixListApplication(RepoApplication):
    repo="prefix-list"
    model=PrefixList
    model_admin=PrefixListAdmin
    menu="Prefix Lists"
