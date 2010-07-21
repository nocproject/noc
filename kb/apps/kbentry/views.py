# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KBEntry Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.kb.models import KBEntry,KBEntryAttachment,KBEntryTemplate
import re
##
## Inline Admin for Attachments
##
class KBEntryAttachmentForm(forms.ModelForm):
    class Meta:
        model=KBEntryAttachment
##
## Entry attacment admin
##
class KBEntryAttachmentAdmin(admin.TabularInline):
    form=KBEntryAttachmentForm
    model=KBEntryAttachment
    extra=3
##
## Admin for Entries
##
class KBEntryAdmin(admin.ModelAdmin):
    list_display=["id","subject"]
    search_fields=["id","subject"]
    inlines=[KBEntryAttachmentAdmin]
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

##
## KBEntry application
##
class KBEntryApplication(ModelApplication):
    model=KBEntry
    model_admin=KBEntryAdmin
    menu="Setup | Entries"
    ##
    rx_template_var=re.compile("{{([^}]+)}}",re.MULTILINE)
    ##
    ##
    ##
    def view_change(self,request,object_id,extra_context=None):
        def response_change(*args):
            self.message_user(request,"KB%s was changed successfully"%object_id)
            return self.response_redirect("kb:view:view",object_id)
        self.admin.response_change=response_change
        return self.admin.change_view(request,object_id,self.get_context(extra_context))
    view_change.url=r"^(\d+)/$"
    view_change.url_name="change"
    view_change.access=HasPerm("change")
    ##
    ## Display the list of templates
    ##
    def view_template_index(self,request):
        templates=KBEntryTemplate.objects.order_by("name")
        return self.render(request,"template_index.html", {"templates":templates})
    view_template_index.url=r"^from_template/$"
    view_template_index.menu="New from Template"
    view_template_index.access=HasPerm("add")
    ##
    ## Create new entry from template
    ##
    def view_from_template(self,request,template_id):
        def expand(template,vars):
            return self.rx_template_var.sub(lambda x:vars[x.group(1)],template)
        template=get_object_or_404(KBEntryTemplate,id=int(template_id))
        var_list=template.var_list
        if var_list and not request.POST:
            return self.render(request,"template_form.html", {"template":template,"vars":var_list})
        subject=template.subject
        body=template.body
        if var_list and request.POST:
            vars={}
            for v in var_list:
                vars[v]=request.POST.get(v,"(((UNDEFINED)))")
            subject=expand(subject,vars)
            body=expand(body,vars)
        kbe=KBEntry(subject=subject,body=body,language=template.language,markup_language=template.markup_language)
        kbe.save(user=request.user)
        kbe.tags=template.tags
        kbe.save(user=request.user)
        return self.response_redirect_to_object(kbe)
    view_from_template.url=r"^from_template/(?P<template_id>\d+)/$"
    view_from_template.url_name="from_template"
    view_from_template.access=HasPerm("add")
