# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KBUserBookmark Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication
from noc.kb.models import KBUserBookmark
##

##
## KBUserBookmark admin
##
class KBUserBookmarkAdmin(admin.ModelAdmin):
    def queryset(self,request):
        return KBUserBookmark.objects.filter(user=request.user)

    def has_change_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self,request)

    def has_delete_permission(self,request,obj=None):
        return self.has_change_permission(request,obj)
        
    def save_model(self, request, obj, form, change):
        obj.user=request.user
        obj.save()
        
##
## KBUserBookmark application
##
class KBUserBookmarkApplication(ModelApplication):
    model=KBUserBookmark
    model_admin=KBUserBookmarkAdmin
    menu="Setup | User Bookmark"
