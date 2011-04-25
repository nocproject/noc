# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Return navigation menu's JSON
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.cache import patch_response_headers
from django.contrib.auth.models import User
## NOC modules
from noc.lib.app import Application, PermitLogged, site, view

##
## NOC's navigation menu
##
class MenuApplication(Application):
    S_ATTR = "__noc_menu"
    MENU_CACHE_TIME = 600  # @todo: Should be settable from config

    def build_user_menu(self, request):
        """Prepare user's personal menu"""
        m = []
        for app_menu in site.menu:
            # Build menu
            items = [(title, url) for title, url, access in app_menu.items if access(request.user)]
            # Build submenus
            for sm in app_menu.submenus:
                si=[(title, url) for title, url, access in sm.items if access(request.user)]
                if si:
                    items += [(sm.title, {"items": si})]
            if items:
                m+=[{"items":items, "app":app_menu.app, "title":app_menu.title}]
        return m

    @view(url=r"^json/(?P<user_id>\d+)/$", url_name="json", access=PermitLogged())
    def view_json(self, request, user_id):
        """Render user's JSON menu data"""
        user = self.get_object_or_404(User, id=int(user_id))
        # Compare with session user
        if user.id != request.user.id:
            return self.response_forbidden()
        # Get menu
        try:
            menu = request.session[self.S_ATTR]
        except KeyError:
            menu = self.build_user_menu(request)
            request.session[self.S_ATTR] = menu
        response = self.render_json(menu)
        patch_response_headers(response, self.MENU_CACHE_TIME)
        return response

