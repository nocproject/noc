# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KB Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import Application, view
from noc.kb.models import *


class IndexAppplication(Application):
    """
    Knowledge base inder
    """
    title = "Knowledge Base"
    TOP_ENTRIES = 20

    def render_index(self, request, entries, tab):
        """
        Render index page for tab
        """
        return self.render(request, "index.html",
            tab=tab, entries=entries,
            tabs=[("bookmarks", "Bookmarks"),
                ("latest", "Last Changed"),
                ("popular", "Popular Articles"),
                ("all", "All Articles")])

    @view(url=r"^$", url_name="index", menu="Knowledge Base", access="launch")
    def view_index(self, request):
        """
        Render index page
        """
        return self.view_index_bookmarks(request)

    @view(url=r"^(?P<tab>[^/]+)/$", url_name="tab", access="launch")
    def view_tab(self, request, tab):
        """
        Render named tab
        """
        tabs = {
            "bookmarks": self.view_index_bookmarks,
            "latest": self.view_index_latest,
            "popular": self.view_index_popular,
            "all": self.view_index_all,
            }
        if tab not in tabs:
            return self.response_not_found("Tab not found")
        return tabs[tab](request)

    @view(url=r"^bookmarks/$", access="launch")
    def view_index_bookmarks(self, request):
        """
        Render bookmarks page
        """
        return self.render_index(request,
                    ([b.kb_entry for b in KBGlobalBookmark.objects.all()] +
                     [b.kb_entry for b
                      in KBUserBookmark.objects.filter(user=request.user)]),
                     "bookmarks")

    @view(url=r"^latest/$", access="launch")
    def view_index_latest(self, request):
        """
        Render last modified page
        """
        return self.render_index(request,
                                 KBEntry.last_modified(self.TOP_ENTRIES),
                                 "latest")

    @view(url=r"^popular/$", access="launch")
    def view_index_popular(self, request):
        """
        Render popular page
        """
        return self.render_index(request,
                                 KBEntry.most_popular(self.TOP_ENTRIES),
                                 "popular")

    @view(url=r"^all/$", access="launch")
    def view_index_all(self, request):
        """
        Render "all" page
        """
        return self.render_index(request,
                                 KBEntry.objects.order_by("-id"), "all")
