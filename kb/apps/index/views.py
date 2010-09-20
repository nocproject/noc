# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KB Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from noc.lib.app import Application,PermitLogged
from noc.kb.models import *
##
## Knowledge Base Index
##
class IndexAppplication(Application):
    title="Knowledge Base"
    TOP_ENTRIES=20
    ##
    ## Render index page
    ##
    def render_index(self,request,entries,tab):
        return self.render(request,"index.html",{
            "tab"    : tab,
            "entries": entries,
            "tabs"   : [("bookmarks", "Bookmarks"),
                ("latest",    "Last Changed"),
                ("popular",   "Popular Articles"),
                ("all",       "All Articles")]})
    ##
    ## Index page
    ##
    def view_index(self,request):
        return self.view_index_bookmarks(request)
    view_index.url=r"^$"
    view_index.url_name="index"
    view_index.menu="Knowledge Base"
    view_index.access=PermitLogged()
    ##
    ## Render named tab
    ##
    def view_tab(self,request,tab):
        tabs={
            "bookmarks" : self.view_index_bookmarks,
            "latest"    : self.view_index_latest,
            "popular"   : self.view_index_popular,
            "all"       : self.view_index_all,
        }
        if tab not in tabs:
            return self.response_not_found("Tab not found")
        return tabs[tab](request)
    view_tab.url=r"^(?P<tab>[^/]+)/$"
    view_tab.url_name="tab"
    view_tab.access=PermitLogged()
    ##
    ## Bookmarks page
    ##
    def view_index_bookmarks(self,request):
        return self.render_index(request,
            [b.kb_entry for b in KBGlobalBookmark.objects.all()]\
            +[b.kb_entry for b in KBUserBookmark.objects.filter(user=request.user)],"bookmarks")
    view_index_bookmarks.url=r"^bookmarks/$"
    view_index_bookmarks.access=PermitLogged()
    ##
    ## Last Modified page
    ##
    def view_index_latest(self,request):
        return self.render_index(request,KBEntry.last_modified(self.TOP_ENTRIES),"latest")
    view_index_latest.url=r"^latest/$"
    view_index_latest.access=PermitLogged()
    ##
    ## Popular page
    ##
    def view_index_popular(self,request):
        return self.render_index(request,KBEntry.most_popular(self.TOP_ENTRIES),"popular")
    view_index_popular.url=r"^popular/$"
    view_index_popular.access=PermitLogged()
    ##
    ## All page
    ##
    def view_index_all(self,request):
        return self.render_index(request,KBEntry.objects.order_by("-id"),"all")
    view_index_all.url=r"^all/$"
    view_index_all.access=PermitLogged()
