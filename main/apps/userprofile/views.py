# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.userprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view, PermitLogged
from noc.main.models import UserProfile
from noc.sa.interfaces.base import (StringParameter, ListOfParameter,
                                    DictParameter, ModelParameter)
from noc.settings import LANGUAGES
from noc.main.models.timepattern import TimePattern
from noc.main.models.notification import USER_NOTIFICATION_METHOD_CHOICES
from noc.main.models.userprofilecontact import UserProfileContact


class UserProfileApplication(ExtApplication):
    """
    main.userprofile application
    """
    title = "User Profile"
    implied_permissions = {
        "launch": ["main:timepattern:lookup"]
    }

    @view(url="^$", method=["GET"], access=PermitLogged(), api=True)
    def api_get(self, request):
        user = request.user
        try:
            profile = user.get_profile()
            language = profile.preferred_language
            theme = profile.theme
            preview_theme = profile.preview_theme
            contacts = [
                {
                    "time_pattern": c.time_pattern.id,
                    "time_pattern__label": c.time_pattern.name,
                    "notification_method": c.notification_method,
                    "params": c.params
                }
                for c in profile.userprofilecontact_set.all()
            ]
        except UserProfile.DoesNotExist:
            language = None
            theme = None
            preview_theme = None
            contacts = []
        return {
            "username": user.username,
            "name": (" ".join(
                [x for x in (user.first_name, user.last_name) if x]
            )).strip(),
            "email": user.email,
            "preferred_language": language,
            "theme": theme,
            "preview_theme": preview_theme,
            "contacts": contacts
        }

    @view(url="^$", method=["POST"], access=PermitLogged(), api=True,
          validate={
              "preferred_language": StringParameter(choices=[x[0] for x in LANGUAGES]),
              "theme": StringParameter(),
              "preview_theme": StringParameter(),
              "contacts": ListOfParameter(
                  element=DictParameter(attrs={
                      "time_pattern": ModelParameter(TimePattern),
                      "notification_method": StringParameter(choices=[x[0] for x in USER_NOTIFICATION_METHOD_CHOICES]),
                      "params": StringParameter()
                  })
              )
          })
    def api_save(self, request, preferred_language, theme,
                 preview_theme, contacts):
        user = request.user
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
        profile.preferred_language = preferred_language
        profile.theme = theme
        profile.preview_theme = preview_theme
        profile.save()
        # Setup contacts
        for c in profile.userprofilecontact_set.all():
            c.delete()
        for c in contacts:
            UserProfileContact(
                user_profile=profile,
                time_pattern=c["time_pattern"],
                notification_method=c["notification_method"],
                params=c["params"]
            ).save()
        # Setup language
        request.session["django_lang"] = preferred_language
        return True
