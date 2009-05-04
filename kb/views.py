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
