# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Repo management application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from noc.lib.app import ModelApplication
from noc.cm.models import Object
import difflib
##
## Repository management application
##
class RepoApplication(ModelApplication):
    repo=None
    ##
    ## Format content for output
    ##
    def render_content(self,object,content):
        return "<pre>%s</pre>"%escape(content).replace("\n","<br/>")
    ##
    ##
    ##
    def view_change(self,request,object_id,revision=None,format="html"):
        if format is None:
            format="html"
        # Check format
        if format not in ("html","text"):
            return self.response_not_found("Invalid format '%s'"%format)
        # Get object
        o=get_object_or_404(Object.get_object_class(self.repo),id=int(object_id))
        # Check permissions
        if not o.has_access(request.user):
            return self.response_forbidden("Access Denied")
        # Check object in repo
        if not o.in_repo:
            return self.render(request,"view.html",{"o":o,"r":[],"content":"Object not ready"})
        # Find revision
        if revision is not None:
            try:
                r=o.find_revision(revision)
            except:
                return self.response_not_found("Revision %s is not found"%revision)
        else:
            r=None
        # Get content
        content=o.get_revision(r)
        # Render content
        if format=="html":
            content=self.render_content(content)
            return self.render(request,"view.html",{"o":o,"r":r,"content":content}) # r????
        else:
            return self.render_plain_text(content)
    view_change.url=r"^(?P<object_id>\d+)/(?:(?P<revision>\d+)/)?(?:(?P<format>text)/)?$"
    view_change.access=ModelApplication.permit_change
    view_change.url_name="view"
    ##
    ## Render diff form
    ##
    def view_diff(request,object_id,mode="u",r1=None,r2=None):
        o=get_object_or_404(Object.get_object_class(self.repo),id=int(object_id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        if request.POST:
            r1=request.POST.get("r1",r1)
            r2=request.POST.get("r2",r2)
        if r1 and r2:
            rev1=o.find_revision(r1)
            rev2=o.find_revision(r2)
            if mode=="2":
                d1=o.get_revision(rev1)
                d2=o.get_revision(rev2)
                d=difflib.HtmlDiff()
                diff=d.make_table(d1.splitlines(),d2.splitlines())
            else:
                diff=o.diff(rev1,rev2)
            return self.render(request,"diff.html",{"o":o,"diff":diff,"r1":r1,"r2":r2,"mode":mode})
        else:
            return self.response_redirect(self.base_url+str(o.id))
    view_diff.url=r"^(?P<object_id>\d+)/diff/(?:(?P<mode>[u2])/(?P<r1>.+)/(?P<r2>.+)/)?$"
    view_diff.access=ModelApplication.permit_change
