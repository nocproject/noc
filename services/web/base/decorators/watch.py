# ----------------------------------------------------------------------
# NotifySubscription handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseAppDecorator
from noc.sa.interfaces.base import BooleanParameter, DateTimeParameter
from noc.main.models.notificationgroup import NotificationGroup


class WatchHandlerDecorator(BaseAppDecorator):
    def contribute_to_class(self):
        self.add_view(
            "api_avail_subscription",
            self.api_avail_subscription,
            method=["GET"],
            url=r"^(?P<object_id>[^/]+)/api_avail_subscription/$",
            access="read",
            api=True,
        )

        self.add_view(
            "api_subscribe_group",
            self.api_subscribe_group,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/watch/(?P<group_id>[0-9a-f]{24})/$",
            access="write",
            api=True,
            validate={
                "expired_at": DateTimeParameter(required=False),
                "suppress": BooleanParameter(default=False),
            },
        )

        self.add_view(
            "api_unsubscribe_group",
            self.api_unsubscribe_group,
            method=["POST"],
            url=r"^(?P<object_id>[^/]+)/unwatch/(?P<group_id>[0-9a-f]{24})/$",
            access="write",
            api=True,
        )

    def api_avail_subscription(self, request, object_id):
        # try:
        #     o = self.app.queryset(request).get(**{self.app.pk: object_id})
        # except self.app.model.DoesNotExist:
        #     return self.app.response_not_found()
        r = []
        for g in NotificationGroup.get_groups_by_user(request.user):
            r += [
                {
                    "id": str(g.id),
                    "label": str(g.label or ""),
                    "description": str(g.description or ""),
                }
            ]
        return r

    def api_subscribe_group(self, request, object_id, group_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        g = NotificationGroup.get_by_id(group_id)
        if not g:
            return self.app.response_not_found()
        g.subscribe(request.user, watch=o)
        return {"status": True}

    def api_unsubscribe_group(self, request, object_id, group_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        g = NotificationGroup.get_by_id(group_id)
        if not g:
            return self.app.response_not_found()
        g.unsubscribe(request.user, watch=o)
        return {"status": True}


def watch_handler(cls):
    WatchHandlerDecorator(cls)
    cls.ng_watch = True
    return cls
