# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPSL Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.cm.repoapp import RepoApplication
from noc.cm.models import RPSL
##
## RPSL admin
##
class RPSLAdmin(admin.ModelAdmin):
    list_display=["repo_path","last_modified","status"]
    search_fields=["repo_path"]
##
## RPSL application
##
class RPSLApplication(RepoApplication):
    repo="rpsl"
    model=RPSL
    model_admin=RPSLAdmin
    menu="RPSL Objects"
