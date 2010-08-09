# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PyRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication
from noc.main.models import PyRule
##
## PyRule admin
##
class PyRuleForm(forms.ModelForm):
    class Meta:
        model=PyRule
    def clean_text(self):
        text=self.cleaned_data["text"]
        try:
            PyRule.compile_text(text)
        except SyntaxError,why:
            raise forms.ValidationError("Syntax Error: "+str(why))
        return text.replace("\r\n","\n")

class PyRuleAdmin(admin.ModelAdmin):
    form=PyRuleForm
    list_display=["name","interface","is_builtin"]
    list_filter=["is_builtin"]
    search_fields=["name"]
##
## PyRule application
##
class PyRuleApplication(ModelApplication):
    model=PyRule
    model_admin=PyRuleAdmin
    menu="Setup | PyRules"
