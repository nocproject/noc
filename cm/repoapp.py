# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Repo management application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from noc.lib.app import ModelApplication,URL,HasPerm,view
from noc.cm.models import Object
from noc.lib.highlight import NOCHtmlFormatter
from pygments.lexers import DiffLexer
from pygments import highlight
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
            r=o.current_revision
        # Get content
        content=o.get_revision(r)
        # Render content
        if format=="html":
            content=self.render_content(o,content)
            return self.render(request,"view.html",{"o":o,"r":r,"content":content})
        else:
            return self.render_plain_text(content)
    view_change.url=[
        URL(r"^(?P<object_id>\d+)/$"                  , name="view"),
        URL(r"^(?P<object_id>\d+)/(?P<revision>\d+)/$", name="view_revision"),
    ]
    view_change.access=HasPerm("view")
    ##
    ##
    ##
    def view_text(self,request,object_id,revision=None):
        return self.view_change(request,object_id,revision,format="text")
    view_text.url=[
        URL(r"^(?P<object_id>\d+)/text/$"                   , name="view_text"),
        URL(r"^(?P<object_id>\d+)/(?P<revision>\d+)/text/$" , name="view_text_revision"),
    ]
    view_text.access=HasPerm("view")
    ##
    ## Render diff form
    ##
    def view_diff(self,request,object_id,mode="u",r1=None,r2=None):
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
                diff=diff.replace("rules=\"groups\"","rules=\"none\"",1) # Use no colgroup rules
            else:
                diff=o.diff(rev1,rev2)
                diff=unicode(diff, "utf8")
                diff=highlight(diff,DiffLexer(),NOCHtmlFormatter()) # Highlight diff
            return self.render(request,"diff.html",{"o":o,"diff":diff,"r1":r1,"r2":r2,"mode":mode})
        else:
            return self.response_redirect_to_object(o)
    view_diff.url=[
        URL(r"^(?P<object_id>\d+)/diff/$",                                        name="diff"),
        URL(r"^(?P<object_id>\d+)/diff/(?P<mode>[u2])/(?P<r1>\d+)/(?P<r2>\d+)/$", name="diff_rev")
    ]
    view_diff.access=HasPerm("view")
    ##
    ##
    ##
    def view_annotate(self,request,object_id):
        o=get_object_or_404(Object.get_object_class(self.repo),id=int(object_id))
        if not o.has_access(request.user):
            return self.response_forbidden("Access denied")
        # Build annotate styles
        last_revision=None
        n=-1
        annotate=[]
        for r,t in o.annotate():
            if r.revision!=last_revision:
                n+=1
                last_revision=r.revision
            annotate+=[("row%d"%(n%2),r,t)]
        return self.render(request,"view.html",{"o":o,"annotate":annotate,"r":o.current_revision})
    view_annotate.url=r"^(?P<object_id>\d+)/annotate/$"
    view_annotate.url_name="annotate"
    view_annotate.access=HasPerm("view")
