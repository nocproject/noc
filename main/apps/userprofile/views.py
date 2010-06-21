# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserProfile Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication,PermitLogged,Deny
from noc.main.models import UserProfile,UserProfileContact


##
## UserProfile Contact Inline
##
class UserProfileContactAdmin(admin.TabularInline):
    extra=5
    model=UserProfileContact
##
## User profile admin
##
class UserProfileAdmin(admin.ModelAdmin):
    inlines=[UserProfileContactAdmin]
    fieldsets=(
        (None, {
            "fields" : ("preferred_language",),
        }),
    )
##
## UserProfile application
##
class UserProfileApplication(ModelApplication):
    model=UserProfile
    model_admin=UserProfileAdmin
    ##
    ## Edit profile
    ##
    def view_change(self,request,extra_context=None):
        def response_change(*args):
            self.message_user(request,"User Profile changed successfully")
            return self.response_redirect("")
        user=request.user
        # Create profile if not exists yet
        try:
            profile=user.get_profile()
        except:
            profile=UserProfile(user=user)
            profile.save()
        self.admin.response_change=response_change
        return self.admin.change_view(request,str(profile.id),self.get_context(extra_context))
    view_change.url=r"^$"
    view_change.url_name="change"
    view_change.access=PermitLogged()
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
    ##
    ##
    def has_change_permission(self,request,obj=None):
        return True

