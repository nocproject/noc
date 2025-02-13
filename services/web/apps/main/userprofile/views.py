# ---------------------------------------------------------------------
# main.userprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view, PermitLogged
from noc.sa.interfaces.base import StringParameter, ListOfParameter, DictParameter, ModelParameter
from noc.settings import LANGUAGES
from noc.main.models.timepattern import TimePattern
from noc.aaa.models.usercontact import UserContact
from noc.main.models.notificationgroup import USER_NOTIFICATION_METHOD_CHOICES, NotificationGroup
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
        subscription_settings = []
        for g in NotificationGroup.get_groups_by_user(user):
            ss = {
                "notification_group": str(g.id),
                "notification_group__label": g.name,
                "user_policy": "A",
                "time_pattern": None,
                "supress": False,
                "preferred_method": "",
                "expired_at": None,
                "title_tag": None,
                "message_types": [t["message_type"] for t in g.message_types],
            }
            uc = g.get_subscription_by_user(user)
            if not uc:
                subscription_settings.append(ss)
                continue
            if uc.time_pattern:
                ss["time_pattern"] = uc.time_pattern.id
                ss["time_pattern__label"] = uc.time_pattern.name
            ss.update(
                {
                    "user_policy": "A",
                    "supress": uc.suppress,
                    "expired_at": uc.expired_at,
                    "title_tag": "",
                }
            )
            subscription_settings.append(ss)
        return {
            "username": user.username,
            "name": (" ".join([x for x in (user.first_name, user.last_name) if x])).strip(),
            "email": user.email,
            "preferred_language": language or "en",
            "contacts": contacts,
            "groups": [g.name for g in user.groups.all().order_by("name")],
            "subscription_settings": subscription_settings,
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
