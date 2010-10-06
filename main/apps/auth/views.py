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
from django.contrib.auth.views import password_change, AuthenticationForm
from noc.lib.app import Application,Permit,PermitLogged
from noc.main.models import PyRule
from noc.settings import AUTH_FORM_PYRULE

class AuthApplication(Application):
    ##
    ## Display and process django's login form
    ##
    def view_login(self,request):
        # Get authentication form class
        authentication_form=PyRule.call(AUTH_FORM_PYRULE if AUTH_FORM_PYRULE else "auth_form_user_password")
        return django_login(request,template_name=self.get_template_path("login.html"),
            redirect_field_name=REDIRECT_FIELD_NAME,authentication_form=authentication_form)
    view_login.url=r"^login/$"
    view_login.access=Permit()
    ##
    ## Close django session and redirect to
    ## the main page
    ##
    def view_logout(self,request):
        django_logout(request)
        return self.response_redirect("/")
    view_logout.url=r"^logout/$"
    view_logout.url_name="logout"
    view_logout.access=PermitLogged()
    ##
    ## Change password
    ##
    def view_change_password(self,request):
        return password_change(request,
            template_name=self.get_template_path("password_change_form.html"),
            post_change_redirect=self.reverse("main:message:success")+"?subject=Password%20changed")
    view_change_password.url=r"^change_password/$"
    view_change_password.url_name="change_password"
    view_change_password.access=PermitLogged()
