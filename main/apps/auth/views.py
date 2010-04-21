# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Login/Logout/password change application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib.auth import logout as django_logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import login as django_login
from noc.lib.app import Application

class AuthApplication(Application):
    ##
    ## Display and process django's login form
    ##
    def view_login(self,request):
        return django_login(request,template_name=self.get_template_path("login.html"),redirect_field_name=REDIRECT_FIELD_NAME)
    view_login.url=r"^login/$"
    view_login.access=Application.permit
    ##
    ## Close django session and redirect to
    ## the main page
    ##
    def view_logout(self,request):
        django_logout(request)
        return self.response_redirect("/")
    view_logout.url=r"^logout/$"
    view_logout.url_name="logout"
    view_logout.access=Application.permit_logged
