# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Group Group Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import ModelApplication
from django.contrib.auth.models import Group
from django import forms
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from noc.main.apps.user.widgets import AccessWidget
from noc.main.models import Permission
##
##
##
class GroupChangeForm(forms.ModelForm):
    noc_group_permissions=forms.CharField(label="Group Access",widget=AccessWidget,required=False)
    class Meta:
        model = Group
    def __init__(self,*args,**kwargs):
        super(GroupChangeForm,self).__init__(*args,**kwargs)
        if "instance" in kwargs:
            self.initial["noc_group_permissions"]="group:"+self.initial["name"]
        self.new_perms=set()
        if args:
            # Fetch posted permissions
            self.new_perms=set([p[5:] for p in args[0] if p.startswith("perm_")])
    def save(self,commit=True):
        model=super(GroupChangeForm,self).save(commit)
        if not model.id:
            model.save()
        Permission.set_group_permissions(model,self.new_perms)
        return model

##
## Admin for groups
##
class GroupAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Access'), {'fields': ('noc_group_permissions',), "classes":["collapse"]}),
    )
    search_fields = ('name',)
    ordering = ('name',)
    list_display = ("name",)
    form = GroupChangeForm
##
##
##
class GroupApplication(ModelApplication):
    model=Group
    model_admin=GroupAdmin
    menu="Setup | Groups"
    icon = "icon_group"
