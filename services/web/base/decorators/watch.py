# ----------------------------------------------------------------------
# NotifySubscription handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseAppDecorator
from noc.sa.interfaces.base import BooleanParameter, DictListParameter, StringParameter
from noc.main.models.notificationgroup import NotificationGroup
from noc.aaa.models.user import User
from noc.crm.models.subscriber import Subscriber


class WatchHandlerDecorator(BaseAppDecorator):
    # update_subscription <oid>/<ng_id>/<subscr_id>/update/ - {contact_id, suppress - true/false

    def contribute_to_class(self):
        self.add_view(
            "api_object_subscriptions",
            self.api_object_subscriptions,
            method=["GET"],
            url=r"^(?P<object_id>[^/]+)/object_subscription/$",
            access="read",
            api=True,
        )

        self.add_view(
            "api_update_object_subscriptions",
            self.api_update_object_subscriptions,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/object_subscription/(?P<group_id>\d+)/update/$",
            access="update_subscription",
            api=True,
            validate={
                "users": DictListParameter(
                    attrs={
                        "user": StringParameter(required=True),
                        "suppress": BooleanParameter(required=False),
                    },
                ),
                "crm_users": DictListParameter(
                    attrs={
                        "user": StringParameter(required=True),
                        "suppress": BooleanParameter(required=False),
                    }
                ),
            },
        )

        self.add_view(
            "api_add_group_subscription",
            self.api_subscribe_group,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/object_subscription/(?P<group_id>\d+)/subscribe/$",
            access="write",
            api=True,
        )
        self.add_view(
            "api_remove_group_subscription",
            self.api_unsubscribe_group,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/object_subscription/(?P<group_id>\d+)/unsubscribe/$",
            access="write",
            api=True,
        )
        self.add_view(
            "api_supress_group_subscription",
            self.api_suppress_group,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/object_subscription/(?P<group_id>\d+)/supress/$",
            access="write",
            api=True,
        )

    @staticmethod
    def subscription_to_dict(s, o, user):
        r = {
            "source": "S" if not s.remote_system else str(s.remote_system.name),
            "remote_system": None if not s.remote_system else str(s.remote_system.id),
            "object": str(o.id),
            "notification_group": str(s.notification_group.id),
            "notification_group__label": str(s.notification_group.name),
            "users": [],
            "crm_users": [],
            "me_subscribe": False,
            "me_suppress": False,
            "allow_edit": True,
            "allow_suppress": True,
        }
        for w in s.get_watchers():
            if user == w:
                r["me_subscribe"] = True
            if isinstance(w, User):
                r["users"].append({"user": str(w.id), "user__label": w.username, "suppress": False})
            else:
                r["crm_users"].append({"user": str(w.id), "user__label": w.name, "suppress": False})
        return r

    def api_object_subscriptions(self, request, object_id):
        r = []
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        proccessed = set()
        for s in NotificationGroup.iter_object_subscription_settings(o):
            r.append(self.subscription_to_dict(s, o, request.user))
            proccessed.add(str(s.notification_group.id))
        for g in NotificationGroup.objects.filter():
            if str(g.id) in proccessed:
                continue
            r.append(
                {
                    "source": "G",
                    "remote_system": None,
                    "object": str(o.id),
                    "notification_group": str(g.id),
                    "notification_group__label": str(g.name),
                    "users": [],
                    "crm_users": [],
                    "me_subscribe": False,  # User Group settings
                    "me_suppress": False,  # User Group settings
                    "allow_edit": False,
                    "allow_suppress": True,
                }
            )
        return r

    def api_update_object_subscriptions(
        self,
        request,
        object_id,
        group_id,
        users=None,
        crm_users=None,
    ):
        """"""
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        group = self.app.get_object_or_404(NotificationGroup, id=group_id)
        watchers, suppresses = [], []
        for c in users or []:
            u = User.get_by_id(int(c["user"]))
            if u and c["suppress"]:
                suppresses.append(u)
            elif u:
                watchers.append(u)
        for c in crm_users or []:
            u = Subscriber.get_by_id(c["user"])
            if u and c["suppress"]:
                suppresses.append(u)
            elif u:
                watchers.append(u)
        s = group.update_subscription(o, watchers=watchers, suppresses=suppresses)
        return {"success": True, "data": self.subscription_to_dict(s, o, request.user)}

    def api_subscribe_group(self, request, object_id, group_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        group = self.app.get_object_or_404(NotificationGroup, id=group_id)
        group.subscribe_object(o, user=request.user)
        return {"success": True}

    def api_unsubscribe_group(self, request, object_id, group_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        group = self.app.get_object_or_404(NotificationGroup, id=group_id)
        group.unsubscribe_object(o, user=request.user)
        return {"success": True}

    def api_suppress_group(self, request, object_id, group_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        group = self.app.get_object_or_404(NotificationGroup, id=group_id)
        group.supress_object(o, user=request.user)
        return {"success": True}


def watch_handler(cls):
    WatchHandlerDecorator(cls)
    cls.ng_watch = True
    return cls
