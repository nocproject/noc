# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Return navigation menu's JSON
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.utils.cache import patch_response_headers
from django.core.cache import cache
from noc.lib.app import Application,PermitLogged,site

MENU_CACHE_TIME=600 # Should be settable from config
##
## NOC's navigation menu
##
class MenuApplication(Application):
    ##
    ## Prepare user's personal menu
    ##
    def build_user_menu(self,request):
        m=[]
        for app_menu in site.menu:
            # Build menu
            items=[(title,url) for title,url,access in app_menu.items if access(request.user)]
            # Build submenus
            for sm in app_menu.submenus:
                si=[(title,url) for title,url,access in sm.items if access(request.user)]
                if si:
                    items+=[(sm.title,{"items":si})]
            if items:
                m+=[{"items":items,"app":app_menu.app,"title":app_menu.title}]
        return m
    ##
    ## Return user's JSON menu description
    ##
    def view_json(self,request):
        cache_key="menu:%d"%request.user.id
        menu=cache.get(cache_key)
        if menu is None:
            menu=self.build_user_menu(request)
            cache.set(cache_key,menu,MENU_CACHE_TIME)
        response=self.render_json(menu)
        patch_response_headers(response,MENU_CACHE_TIME)
        return response
    view_json.url=r"^json/$"
    view_json.url_name="json"
    view_json.access=PermitLogged()
