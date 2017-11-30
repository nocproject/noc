# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# State handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseAppDecorator
from noc.wf.models.transition import Transition


class StateHandlerDecorator(BaseAppDecorator):
    def contribute_to_class(self):
        self.add_view(
            "api_get_transitions",
            self.api_transitions,
            method=["GET"],
            url=r"^(?P<object_id>[^/]+)/transitions/$",
            access="read",
            api=True
        )

        self.add_view(
            "api_make_transition",
            self.api_make_transition,
            method=["GET"],
            url=r"^(?P<object_id>[^/]+)/transitions/(?P<transition_id>[0-9a-f]{24}/$$",
            access="write",
            api=True
        )

    def api_transitions(self, request, object_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        r = []
        for t in Transition.objects.filter(from_state=o.state, enable_manual=True):
            r += [{
                "id": str(t.id),
                "label": str(t.label or ""),
                "description": str(t.description or "")
            }]
        return r

    def api_make_transition(self, request, object_id, transition_id):
        try:
            o = self.app.queryset(request).get(**{self.app.pk: object_id})
        except self.app.model.DoesNotExist:
            return self.app.response_not_found()
        try:
            t = Transition.objects.get(
                from_state=o.state,
                enable_manual=True,
                id=transition_id
            )
        except Transition.DoesNotExist:
            return self.app.response_not_found()
        o.fire_transition(t)


def state_handler(cls):
    StateHandlerDecorator(cls)
    return cls
