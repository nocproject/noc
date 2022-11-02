# ---------------------------------------------------------------------
# main.userprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extapplication import ExtApplication, view, PermitLogged
from noc.sa.interfaces.base import StringParameter, ListOfParameter, DictParameter, ModelParameter
from noc.settings import LANGUAGES
from noc.main.models.timepattern import TimePattern
from noc.aaa.models.usercontact import UserContact
from noc.main.models.notificationgroup import USER_NOTIFICATION_METHOD_CHOICES
from noc.core.translation import ugettext as _


class UserProfileApplication(ExtApplication):
    """
    main.userprofile application
    """

    title = _("User Profile")
    implied_permissions = {"launch": ["main:timepattern:lookup"]}

    @view(url="^$", method=["GET"], access=PermitLogged(), api=True)
    def api_get(self, request):
        user = request.user
        language = user.preferred_language
        contacts = [
            {
                "time_pattern": c.time_pattern.id,
                "time_pattern__label": c.time_pattern.name,
                "notification_method": c.notification_method,
                "params": c.params,
            }
            for c in UserContact.objects.filter(user=user)
        ]
        return {
            "username": user.username,
            "name": (" ".join([x for x in (user.first_name, user.last_name) if x])).strip(),
            "email": user.email,
            "preferred_language": language or "en",
            "contacts": contacts,
            "groups": [g.name for g in user.groups.all().order_by("name")],
        }

    @view(
        url="^$",
        method=["POST"],
        access=PermitLogged(),
        api=True,
        validate={
            "preferred_language": StringParameter(choices=[x[0] for x in LANGUAGES]),
            "contacts": ListOfParameter(
                element=DictParameter(
                    attrs={
                        "time_pattern": ModelParameter(TimePattern),
                        "notification_method": StringParameter(
                            choices=[x[0] for x in USER_NOTIFICATION_METHOD_CHOICES]
                        ),
                        "params": StringParameter(),
                    }
                )
            ),
        },
    )
    def api_save(self, request, preferred_language, contacts):
        user = request.user
        user.preferred_language = preferred_language
        user.save()
        # Setup contacts
        UserContact.objects.filter(user=user).delete()
        for c in contacts:
            UserContact(
                user=user,
                time_pattern=c["time_pattern"],
                notification_method=c["notification_method"],
                params=c["params"],
            ).save()
        return True
