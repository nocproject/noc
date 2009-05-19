# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.cm.models import Object
from django.shortcuts import get_object_or_404
from noc.lib.render import render,render_plain_text
import os
from django.http import HttpResponseNotFound,HttpResponseRedirect,HttpResponseForbidden
from django.utils.html import escape
##
## Display object's revision
##
def view(request,repo,object_id,revision=None,format="html"):
    o=get_object_or_404(Object.get_object_class(repo),id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    revs=o.revisions
    if revision:
        r=None
        for rev in revs:
            if rev.revision==revision:
                r=rev
                break
        if not r:
            return HttpResponseNotFound("Revision not found")
    else:
        if len(revs):
            r=o.revisions[0]
        else:
            r=None
    if r:
        content=o.get_revision(r)
    else:
        content=""
    if format=="html":
        if repo=="config":
            content=o.managed_object.profile.highlight_config(content)
        else:
            content="<pre>%s</pre>"%escape(content).replace("\n","<br/>")
        return render(request,"cm/view.html",{"o":o,"r":r,"content":content})
    elif format=="text":
        return render_plain_text(content)
    else:
        return HttpResponseNotFound("Invalid format: %s"%format)

def diff(request,repo,object_id):
    o=get_object_or_404(Object.get_object_class(repo),id=int(object_id))
    if not o.has_access(request.user):
        return HttpResponseForbidden("Access denied")
    if request.POST and "r1" in request.POST and "r2" in request.POST:
        r1=o.find_revision(request.POST["r1"])
        r2=o.find_revision(request.POST["r2"])
        diff=o.diff(r1,r2)
        return render(request,"cm/diff.html",{"o":o,"diff":diff,"r1":r1,"r2":r2})
    else:
        return HttpResponseRedirect("/cm/view/config/%d/"%o.id)
