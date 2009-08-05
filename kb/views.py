# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.kb.models import *
from noc.lib.render import render
from noc.main.models import MIMEType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django import forms
from django.contrib.auth.decorators import permission_required
import re

##
## Title page
##
def index(request):
    return index_bookmarks(request)
##
## Bookmarks page
##
def index_bookmarks(request):
    entries=[b.kb_entry for b in KBGlobalBookmark.objects.all()]+[b.kb_entry for b in KBUserBookmark.objects.filter(user=request.user)]
    return render(request,"kb/index.html",
        {
        "tab"     : "bookmarks",
        "entries" : entries,
        })
##
## Latest Changes page
##
def index_latest(request):
    return render(request,"kb/index.html",
        {
        "tab"     : "latest",
        "entries" : KBEntry.last_modified(20),
        })
##
## Popular Articles
##
def index_popular(request):
    return render(request,"kb/index.html",
        {
        "tab"     : "popular",
        "entries" : KBEntry.most_popular(20),
        })
##
## All Pages
##
def index_all(request):
    return render(request,"kb/index.html",
    {
        "tab"     : "all",
        "entries" : KBEntry.objects.order_by("-id")
    })
##
##
##
def index_categories(request):
    return render(request,"kb/index.html", 
    {
        "tab"       : "categories",
        "entries"   : KBCategory.objects.order_by("name")
    })
##
##
##
def index_category(request,category_id):
    category=get_object_or_404(KBCategory,id=int(category_id))
    return render(request,"kb/index_category.html",{"category":category,"entries":category.kbentry_set.order_by("id")})
    
##
## KB Entry Preview
##
def view(request,kb_id):
    e=get_object_or_404(KBEntry,id=int(kb_id))
    e.log_preview(request.user)
    return render(request,"kb/view.html",{"e":e,"has_bookmark":e.is_bookmarked(request.user)})
##
## Download attachment
##
def attachment(request,kb_id,name):
    e=get_object_or_404(KBEntry,id=int(kb_id))
    a=get_object_or_404(KBEntryAttachment,kb_entry=e,name=name)
    return HttpResponse(a.file.file.read(),content_type=MIMEType.get_mime_type(a.file.name))
##
## Manipulate user bookmark
##     action is one of "set" or "unset"
##
def bookmark(request,kb_id,action):
    if action not in ("set","unset"):
        return HttpResponseNotFound()
    e=get_object_or_404(KBEntry,id=int(kb_id))
    if action=="set":
        e.set_user_bookmark(request.user)
    else:
        e.unset_user_bookmark(request.user)
    return HttpResponseRedirect("/kb/%d/"%e.id)
##
## Generate template list
##
def template_index(request):
    templates=KBEntryTemplate.objects.order_by("name")
    return render(request,"kb/template_index.html", {"templates":templates})
##
## Create new entry from template
##
rx_template_var=re.compile("{{([^}]+)}}",re.MULTILINE)
@permission_required("kb.change_kbentry")
def from_template(request,template_id):
    def expand(template,vars):
        return rx_template_var.sub(lambda x:vars[x.group(1)],template)
    template=get_object_or_404(KBEntryTemplate,id=int(template_id))
    var_list=template.var_list
    if var_list and not request.POST:
        return render(request,"kb/template_form.html", {"template":template,"vars":var_list})
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
    for c in template.categories.all():
        kbe.categories.add(c)
    return HttpResponseRedirect("/kb/%d/"%kbe.id)
