# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.cm.repoapp import RepoApplication
from noc.cm.models import Config
import datetime
##
## Config admin
##
class ConfigAdmin(admin.ModelAdmin):
    list_display=["repo_path","pull_every","last_modified","next_pull","status"]
    search_fields=["repo_path"]
    fields=["pull_every","next_pull"]
    actions=["get_now"]
    def queryset(self,request):
        return Config.queryset(request.user)
    ##
    ## Schedule selected objects to immediate pull
    ##
    def get_now(self,request,queryset):
        count=0
        now=datetime.datetime.now()
        for o in queryset:
            o.next_pull=now
            o.save()
            count+=1
        if count==1:
            self.message_user(request,"1 config scheduled to immediate fetch")
        else:
            self.message_user(request,"%d configs scheduled to immediate fetch"%count)
##
## Config application
##
class ConfigApplication(RepoApplication):
    repo="config"
    model=Config
    model_admin=ConfigAdmin
    menu="Configs"
    ##
    ## Config highlight
    ##
    def render_content(self,object,content):
        return object.managed_object.profile.highlight_config(content)
