# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIB Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication,HasPerm
from noc.lib.fileutils import temporary_file
from noc.fm.models import MIB,MIBData,MIBRequiredException
##
## MIBData inline
##
class MIBDataInlineAdmin(admin.TabularInline):
    model=MIBData
    extra=0
##
## MIB admin
##
class MIBAdmin(admin.ModelAdmin):
    list_display=["name","last_updated","uploaded"]
    search_fields=["name"]
    inlines=[MIBDataInlineAdmin]
##
## MIB Upload Form
##
class MIBUploadForm(forms.Form):
    file=forms.FileField()
##
## MIB application
##
class MIBApplication(ModelApplication):
    model=MIB
    model_admin=MIBAdmin
    menu="Setup | MIBs"
    class MIBUploadForm(forms.Form):
        file=forms.FileField()
    ##
    ## Upload MIB
    ##
    def view_upload(self,request):
        if request.method=="POST":
            form = MIBUploadForm(request.POST, request.FILES)
            if form.is_valid():
                with temporary_file(request.FILES['file'].read()) as path:
                    try:
                        mib=MIB.load(path)
                    except MIBRequiredException,x:
                        self.message_user(request,"Failed to upload MIB, %s requires %s"%(x.mib,x.requires_mib))
                        return self.response_redirect(self.base_url)
                self.message_user(request,"%s uploaded"%(mib))
                return self.response_redirect_to_object(mib)
        else:
            form=MIBUploadForm()
        return self.render(request,"upload.html",{"form":form})
    view_upload.url=r"^upload/$"
    view_upload.url_name="upload"
    view_upload.access=HasPerm("upload")
