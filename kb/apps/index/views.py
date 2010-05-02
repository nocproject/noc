# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KB Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from noc.lib.app import Application
from noc.kb.models import *
##
## Knowledge Base Index
##
class IndexAppplication(Application):
    TOP_ENTRIES=20
    ##
    ## Render index page
    ##
    def render_index(self,request,entries,tab):
        return self.render(request,"index.html",{
            "tab"    : tab,
            "entries": entries,
            "tabs"   : [("bookmarks", "Bookmarks"),
                ("categories","Categories"),
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
    view_index.access=Application.permit_logged
    ##
    ## Bookmarks page
    ##
    def view_index_bookmarks(self,request):
        return self.render_index(request,
            [b.kb_entry for b in KBGlobalBookmark.objects.all()]\
            +[b.kb_entry for b in KBUserBookmark.objects.filter(user=request.user)],"bookmarks")
    view_index_bookmarks.url=r"^bookmarks/$"
    view_index_bookmarks.access=Application.permit_logged
    ##
    ## Categories page
    ##
    def view_index_categories(self,request):
        return self.render_index(request,KBCategory.objects.order_by("name"),"categories")
    view_index_categories.url=r"^categories/$"
    view_index_categories.url_name="categories"
    view_index_categories.access=Application.permit_logged
    ##
    ## Last Modified page
    ##
    def view_index_latest(self,request):
        return self.render_index(request,KBEntry.last_modified(self.TOP_ENTRIES),"latest")
    view_index_latest.url=r"^latest/$"
    view_index_latest.access=Application.permit_logged
    ##
    ## Popular page
    ##
    def view_index_popular(self,request):
        return self.render_index(request,KBEntry.most_popular(self.TOP_ENTRIES),"popular")
    view_index_popular.url=r"^popular/$"
    view_index_popular.access=Application.permit_logged
    ##
    ## All page
    ##
    def view_index_all(self,request):
        return self.render_index(request,KBEntry.objects.order_by("-id"),"popular")
    view_index_all.url=r"^all/$"
    view_index_all.access=Application.permit_logged
    ##
    ## Category Index
    ##
    def view_index_category(self,request,category_id):
        category=get_object_or_404(KBCategory,id=int(category_id))
        return self.render(request,"index_category.html",{"category":category,"entries":category.kbentry_set.order_by("id")})
    view_index_category.url=r"^categories/(?P<category_id>\d+)/$"
    view_index_category.url_name="category"
    view_index_category.access=Application.permit_logged
