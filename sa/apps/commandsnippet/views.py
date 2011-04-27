# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CommandSnippet Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
from django import forms
from django.template import Template, TemplateSyntaxError
## NOC modules
from noc.lib.app import ModelApplication
from noc.sa.models import CommandSnippet

class CommandSnippetForm(forms.ModelForm):
    """Validation form"""
    class Meta:
        model=CommandSnippet
    
    def clean_snippet(self):
        s = self.cleaned_data["snippet"]
        try:
            Template(s)
        except TemplateSyntaxError, why:
            raise forms.ValidationError("Template syntax error: %s" % why)
        return s
    

class CommandSnippetAdmin(admin.ModelAdmin):
    """CommandSnippet Admin"""
    form = CommandSnippetForm
    list_display = ["name", "is_enabled", "selector", "description",
            "require_confirmation"]
    list_filter = ["require_confirmation", "is_enabled"]


class CommandSnippetApplication(ModelApplication):
    """CommandSnippet application"""
    model = CommandSnippet
    model_admin = CommandSnippetAdmin
    menu = "Setup | Command Snippets"
