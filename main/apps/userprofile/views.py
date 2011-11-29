# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UserProfile Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication, PermitLogged, Deny, view
from noc.main.models import UserProfile, UserProfileContact
from noc import settings

##
## UserProfile Contact Inline
##
class UserProfileContactAdmin(admin.TabularInline):
    extra = 5
    model = UserProfileContact
##
## User profile admin
##
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [UserProfileContactAdmin]
    fieldsets = (
        (None, {
            "fields": ("preferred_language", "theme"),
        }),
    )
##
## UserProfile application
##
class UserProfileApplication(ModelApplication):
    model = UserProfile
    model_admin = UserProfileAdmin
    ##
    ## Edit profile
    ##
    @view(method=["GET", "POST"], url=r"^profile/$", access=PermitLogged())
    def view_change(self, request, extra_context=None):
        def setup_language():
            # Change session language
            lang = settings.LANGUAGE_CODE
            profile = request.user.get_profile()
            if profile and profile.preferred_language:
                lang = profile.preferred_language
            request.session["django_language"] = lang

        def response_change(*args):
            setup_language()
            self.message_user(request, "User Profile changed successfully")
            return self.response_redirect("")

        user = request.user
        # Create profile if not exists yet
        try:
            profile = user.get_profile()
        except:
            profile = UserProfile(user=user)
            profile.save()
        self.admin.response_change = response_change
        r = self.admin.change_view(request, str(profile.id),
                                      self.get_context(extra_context))
        setup_language()
        return r


    def has_delete_permission(self, request, obj=None):
        """Disable delete"""
        return False

    def has_add_permission(self, request):
        """Disable add"""
        return False

    def has_change_permission(self, request, obj=None):
        return True
