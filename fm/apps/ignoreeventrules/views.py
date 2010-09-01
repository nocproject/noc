# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IgnoreEventRules Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication
from noc.fm.models import IgnoreEventRules
import re
##
## Validation form
##
class IgnoreEventRulesForm(forms.ModelForm):
    class Meta:
        model=IgnoreEventRules
    ## Check regular expression
    def clean_left_re(self):
        left_re=self.cleaned_data["left_re"]
        try:
            re.compile(left_re)
        except:
            raise forms.ValidationError("Invalid regular expression")
        return left_re
    ## Check regular expression
    def clean_right_re(self):
        right_re=self.cleaned_data["right_re"]
        try:
            re.compile(right_re)
        except:
            raise forms.ValidationError("Invalid regular expression")
        return right_re
##
## IgnoreEventRules admin
##
class IgnoreEventRulesAdmin(admin.ModelAdmin):
    form=IgnoreEventRulesForm
    list_display=["name","is_active","left_re","right_re","description"]
    search_fields=["name","description","left_re","right_re"]
    list_filter=["is_active"]
##
## IgnoreEventRules application
##
class IgnoreEventRulesApplication(ModelApplication):
    model=IgnoreEventRules
    model_admin=IgnoreEventRulesAdmin
    menu="Setup | Ignore Event Rules"
