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
from django.http import HttpResponse,HttpResponseNotFound
from django import forms

##
## Title page
##
def index(request):
    return index_latest(request)
##
##
##
def index_latest(request):
    return render(request,"kb/index.html",
        {
        "tab"     : "latest",
        "entries" : KBEntry.last_modified(20),
        })
##
##
##
def index_popular(request):
    return render(request,"kb/index.html",
        {
        "tab"     : "popular",
        "entries" : KBEntry.most_popular(20),
        })
##
##
##
def index_all(request):
    return render(request,"kb/index.html",
    {
        "tab"     : "all",
        "entries" : KBEntry.objects.order_by("-id")
    })
##
## KB Entry Preview
##
def view(request,kb_id):
    e=get_object_or_404(KBEntry,id=int(kb_id))
    e.log_preview(request.user)
    return render(request,"kb/view.html",{"e":e})
##
## Download attachment
##
def attachment(request,kb_id,name):
    e=get_object_or_404(KBEntry,id=int(kb_id))
    a=get_object_or_404(KBEntryAttachment,kb_entry=e,name=name)
    return HttpResponse(a.file.file.read(),content_type=MIMEType.get_mime_type(a.file.name))
