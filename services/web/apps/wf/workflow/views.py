# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# wf.workflow application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State
from noc.wf.models.transition import Transition
from noc.core.translation import ugettext as _


class WorkflowApplication(ExtDocApplication):
    """
    Workflow application
    """
    title = _("Workflows")
    menu = [_("Setup"), _("Workflow")]
    model = Workflow

    @view("^(?P<id>[0-9a-f]{24})/config/",
          method=["GET"], access="write", api=True)
    def get_config(self, request, id):
        wf = self.get_object_or_404(Workflow, id)
        r = {
            "name": wf.name,
            "description": wf.description,
            "states": [],
            "transitions": []
        }
        for state in State.objects.filter(workflow=wf.id):
            sr = {
                "name": state.name,
                "description": state.description,
                "is_default": state.is_default,
                "is_productive": state.is_productive,
                "update_last_seen": state.update_last_seen,
                "ttl": state.ttl,
                "update_expired": state.update_expired,
                "on_enter_handlers": state.on_enter_handlers,
                "job_handler": state.job_handler,
                "on_leave_handlers": state.on_leave_handlers
            }
            r["states"] += [sr]
        for t in Transition.objects.filter(workflow=wf.id):
            tr = {
                "from_state": t.from_state.name,
                "to_state": t.to_state.name,
                "is_active": t.is_active,
                "event": t.event,
                "label": t.label,
                "description": t.description,
                "enable_manual": t.enable_manual,
                "handlers": t.handlers
            }
            r["transitions"] += [tr]
        return r
