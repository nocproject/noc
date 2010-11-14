# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.contrib import admin
## NOC modules
from noc.cm.repoapp import RepoApplication, HasPerm, ModelApplication, view
from noc.sa.models import TaskSchedule
from noc.cm.models import Config
##
## Config admin
##
class ConfigAdmin(admin.ModelAdmin):
    list_display=["repo_path","pull_every","last_modified","next_pull","status","change_link"]
    search_fields=["repo_path"]
    fields=["pull_every","next_pull"]
    actions=["get_now"]
    def queryset(self,request):
        return Config.queryset(request.user)
    
    ##
    ## Schedule selected objects to immediate pull
    ##
    def get_now(self,request,queryset):
        # Change next_pull
        count=0
        now=datetime.datetime.now()
        for o in queryset:
            o.next_pull=now
            o.save()
            count+=1
        # Rechedule cm.config_pull
        TaskSchedule.reschedule("cm.config_pull")
        # Notify user
        if count==1:
            self.message_user(request,"1 config scheduled to immediate fetch")
        else:
            self.message_user(request,"%d configs scheduled to immediate fetch"%count)
    
    ##
    ## Delele "delete_selected"
    ##
    def get_actions(self,request):
        actions=super(ConfigAdmin,self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
    

##
## Config application
##
class ConfigApplication(RepoApplication):
    repo="config"
    model=Config
    model_admin=ConfigAdmin
    menu="Configs"
    ##
    ## cm:config:change handler
    ##
    @view(  url=r"^(?P<object_id>\d+)/change/$",
            url_name="change",
            access=HasPerm("change_settings"))
    def view_change_settings(self,request,object_id):
        def response_change(*args):
            self.message_user(request,"Parameters was changed successfully")
            return self.response_redirect("cm:config:changelist")
        self.admin.response_change=response_change
        return ModelApplication.view_change(self,request,object_id)
    
    ##
    ## Disable delete
    ##
    def has_delete_permission(self,request,obj=None):
        return False
    
    ##
    ## Disable add
    ##
    def has_add_permission(self,request):
        return False
    
    ##
    ## Config highlight
    ##
    def render_content(self,object,content):
        return object.managed_object.profile.highlight_config(content)
    
