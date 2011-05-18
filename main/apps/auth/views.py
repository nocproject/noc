# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Login/Logout/password change application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib.auth import logout as django_logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import login as django_login
from django.contrib.auth.views import password_change, AuthenticationForm
## NOC modules
from noc.lib.app import Application, Permit, PermitLogged, view
from noc.main.models import PyRule
from noc.settings import AUTH_FORM_PYRULE, LANGUAGE_CODE
from noc.lib.middleware import set_user


class AuthApplication(Application):
    @view(url=r"^login/", access=Permit())
    def view_login(self, request):
        """
        Display and process login form. Set up user language
        on successful login
        """
        # Get authentication form class
        authentication_form = PyRule.call(AUTH_FORM_PYRULE if AUTH_FORM_PYRULE else "auth_form_user_password")
        
        r = django_login(request,
                         template_name=self.get_template_path("login.html"),
                         redirect_field_name=REDIRECT_FIELD_NAME,
                         authentication_form=authentication_form)
        if request.user.is_authenticated():
            # Write actual user into TLS cache
            set_user(request.user)
            # Set up session language
            lang = LANGUAGE_CODE
            profile = request.user.get_profile()
            if profile and profile.preferred_language:
                lang = profile.preferred_language
            request.session["django_language"] = lang
        return r

    @view(url=r"^logout/$", url_name="logout", access=PermitLogged())
    def view_logout(self, request):
        """
        Close django's session and redirect to the main page
        """
        django_logout(request)
        return self.response_redirect("/")

    @view(url=r"^change_password/$", url_name="change_password",
          access=PermitLogged())
    def view_change_password(self, request):
        """
        Change password form
        """
        return password_change(request,
            template_name=self.get_template_path("password_change_form.html"),
            post_change_redirect=(self.reverse("main:message:success") +
                                  "?subject=Password%20changed"))
