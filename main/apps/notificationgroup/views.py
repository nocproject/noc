# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NotificationGroup Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.main.models import NotificationGroup,NotificationGroupUser,NotificationGroupOther
##
## Notification Groups Admin
##
class NotificationGroupUserAdmin(admin.TabularInline):
    extra=5
    model=NotificationGroupUser

class NotificationGroupOtherAdmin(admin.TabularInline):
    extra=5
    model=NotificationGroupOther

class NotificationGroupAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
    actions=["test_notifications"]
    inlines=[NotificationGroupUserAdmin,NotificationGroupOtherAdmin]
    
    def test_notifications(self,request,queryset):
        return self.app.response_redirect("test/%s/"%",".join([str(p.id) for p in queryset]))
    test_notifications.short_description="Test selected Notification Groups"
##
## NotificationGroup application
##
class NotificationGroupApplication(ModelApplication):
    model=NotificationGroup
    model_admin=NotificationGroupAdmin
    menu="Setup | Notification Groups"
    ##
    ## Test Selectors
    ##
    class TestForm(forms.Form):
        subject=forms.CharField()
        body=forms.CharField(widget=forms.Textarea)
    def view_test(self,request,groups):
        groups=[get_object_or_404(NotificationGroup,id=int(x)) for x in groups.split(",")]
        if request.POST:
            form=self.TestForm(request.POST)
            if form.is_valid():
                for g in groups:
                    g.notify(subject=form.cleaned_data["subject"],body=form.cleaned_data["body"])
                self.message_user(request,"Test messages are sent")
                return self.response_redirect("main:notificationgroup:changelist")
        else:
            form=self.TestForm()
        return self.render(request,"test.html",{"form":form,"groups":groups})
    view_test.url=r"^test/(?P<groups>\d+(?:,\d+)*)/$"
    view_test.access=HasPerm("change")

