# ----------------------------------------------------------------------
# wf.workflow application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from copy import deepcopy

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State
from noc.wf.models.transition import Transition, TransitionVertex
from noc.core.translation import ugettext as _
from noc.models import get_model
from noc.sa.interfaces.base import (
    StringParameter,
    IntParameter,
    DictListParameter,
    BooleanParameter,
    StringListParameter,
)


class WorkflowApplication(ExtDocApplication):
    """
    Workflow application
    """

    title = _("Workflows")
    menu = [_("Setup"), _("Workflow")]
    model = Workflow

    NEW_ID = "000000000000000000000000"

    @view(r"^(?P<id>[0-9a-f]{24})/config/", method=["GET"], access="write", api=True)
    def api_get_config(self, request, id):
        wf = self.get_object_or_404(Workflow, id=id)
        r = {
            "id": str(wf.id),
            "name": wf.name,
            "is_active": wf.is_active,
            "description": wf.description,
            "states": [],
            "allowed_models": [{"id": am, "label": am} for am in wf.allowed_models],
            "transitions": [],
        }
        for state in State.objects.filter(workflow=wf.id):
            sr = {
                "id": str(state.id),
                "name": state.name,
                "description": state.description,
                "is_default": state.is_default,
                "is_productive": state.is_productive,
                "is_wiping": state.is_wiping,
                "update_last_seen": state.update_last_seen,
                "ttl": state.ttl,
                "update_expired": state.update_expired,
                "on_enter_handlers": state.on_enter_handlers,
                "job_handler": state.job_handler,
                "on_leave_handlers": state.on_leave_handlers,
                "labels": [
                    self.format_label(ll)
                    for ll in Label.objects.filter(name__in=state.labels).order_by("display_order")
                ],
                "bi_id": str(state.bi_id) if state.bi_id else None,
                "x": state.x,
                "y": state.y,
            }
            r["states"] += [sr]
        for t in Transition.objects.filter(workflow=wf.id):
            tr = {
                "id": str(t.id),
                "from_state": t.from_state.name,
                "to_state": t.to_state.name,
                "is_active": t.is_active,
                "event": t.event,
                "label": t.label,
                "description": t.description,
                "enable_manual": t.enable_manual,
                "handlers": t.handlers,
                "required_rules": [
                    {
                        "labels": [
                            self.format_label(ll)
                            for ll in Label.objects.filter(name__in=rr.labels).order_by(
                                "display_order"
                            )
                        ],
                        "exclude_labels": [],
                    }
                    for rr in t.required_rules
                ],
                "vertices": [{"x": v.x, "y": v.y} for v in t.vertices],
                "bi_id": str(t.bi_id) if t.bi_id else None,
            }
            r["transitions"] += [tr]
        return r

    @view(
        r"^(?P<id>[0-9a-f]{24})/config/",
        method=["POST"],
        access="write",
        api=True,
        validate={
            "name": StringParameter(),
            "description": StringParameter(default=""),
            "is_active": BooleanParameter(default=False),
            "allowed_models": StringListParameter(),
            "states": DictListParameter(
                attrs={
                    "id": StringParameter(default=""),
                    "name": StringParameter(),
                    "description": StringParameter(default=""),
                    "is_default": BooleanParameter(default=False),
                    "is_productive": BooleanParameter(default=False),
                    "is_wiping": BooleanParameter(default=False),
                    "update_last_seen": BooleanParameter(default=False),
                    "ttl": IntParameter(default=0),
                    "update_expired": BooleanParameter(default=False),
                    "on_enter_handlers": StringListParameter(),
                    "job_handler": StringParameter(required=False),
                    "labels": StringListParameter(required=False),
                    "on_leave_handlers": StringListParameter(),
                    "x": IntParameter(),
                    "y": IntParameter(),
                }
            ),
            "transitions": DictListParameter(
                attrs={
                    "id": StringParameter(default=""),
                    "from_state": StringParameter(),
                    "to_state": StringParameter(),
                    "is_active": BooleanParameter(default=False),
                    "event": StringParameter(required=False),
                    "label": StringParameter(),
                    "description": StringParameter(default=""),
                    "enable_manual": BooleanParameter(),
                    "required_rules": DictListParameter(
                        attrs={
                            "labels": StringListParameter(),
                            "exclude_labels": StringListParameter(),
                        },
                        required=False,
                    ),
                    "handlers": StringListParameter(),
                    "vertices": DictListParameter(attrs={"x": IntParameter(), "y": IntParameter()}),
                }
            ),
        },
    )
    def api_save_config(
        self,
        request,
        id,
        name,
        description,
        is_active,
        states,
        transitions,
        allowed_models,
        **kwargs,
    ):
        if id == self.NEW_ID:
            wf = Workflow()
        else:
            wf = self.get_object_or_404(Workflow, id=id)
        # Update workflow
        wf.name = name
        wf.description = description
        wf.is_active = is_active
        wf.allowed_models = []
        for am in allowed_models:
            try:
                get_model(am)
            except ImportError:
                raise ValueError("Bad Model: %s" % am)
            wf.allowed_models += [am]
        wf.save()
        # Get current state
        current_states = {}  # str(id) -> state
        for st in State.objects.filter(workflow=wf.id):
            current_states[str(st.id)] = st
        # Synchronize states
        seen_states = set()
        state_names = {}  # name -> state
        for s in states:
            state = None
            if s["id"]:
                # Existing state
                seen_states.add(s["id"])
                state = current_states.get(s["id"])
            if not hasattr(s, "workflow"):
                s["workflow"] = wf.id
            # Update state attributes
            if not state:
                state = State()
                changed = True
            else:
                changed = False
            for k in s:
                if k in ("id", "bi_id"):
                    continue
                if getattr(state, k) != s[k]:
                    setattr(state, k, s[k])
                    changed = True
            if changed:
                state.save()
            state_names[state.name] = state
        # Get current transitions
        current_transitions = {}  # str(id) -> transition
        for ct in Transition.objects.filter(workflow=wf.id):
            current_transitions[str(ct.id)] = ct
        # Synchronize transitions
        seen_transitions = set()
        for t in transitions:
            transition = None
            if t["id"]:
                # Existing transitions
                seen_transitions.add(t["id"])
                transition = current_transitions.get(t["id"])
            # Update transition attributes
            if not transition:
                transition = Transition(workflow=wf)
                changed = True
            else:
                changed = False
            for k in t:
                if k in ("id", "bi_id"):
                    continue
                elif k in ("from_state", "to_state"):
                    t[k] = state_names[t[k]]
                elif k == "vertices":
                    t[k] = [TransitionVertex(x=vx["x"], y=vx["y"]) for vx in t[k]]
                old = getattr(transition, k)
                if old != t[k]:
                    setattr(transition, k, t[k])
                    changed = True
            if changed:
                transition.save()
        # Delete hanging transitions
        for tid in set(current_transitions) - seen_transitions:
            current_transitions[tid].delete()
        # Delete hanging state
        for sid in set(current_states) - seen_states:
            current_states[sid].delete()

    rx_clone_name = re.compile(r"\(Copy #(\d+)\)$")

    @view(r"^(?P<id>[0-9a-f]{24})/clone/", method=["POST"], access="write", api=True)
    def api_clone(self, request, id):
        wf = self.get_object_or_404(Workflow, id=id)
        # Get all clone names
        m = 0
        for d in Workflow._get_collection().find(
            {"name": {"$regex": re.compile(r"^%s\(Copy #\d+\)$" % re.escape(wf.name))}},
            {"_id": 0, "name": 1},
        ):
            match = self.rx_clone_name.search(d["name"])
            if match:
                n = int(match.group(1))
                if n > m:
                    m = n
        # Generate name
        name = "%s (Copy #%d)" % (wf.name, m + 1)
        # Clone workflow
        new_wf = deepcopy(wf)
        new_wf.name = name
        new_wf.allowed_models = []
        new_wf.id = None
        new_wf.bi_id = None
        new_wf.save()
        # Clone states
        smap = {}  # old id -> new state
        for state in State.objects.filter(workflow=wf.id):
            new_state = deepcopy(state)
            new_state.workflow = new_wf
            new_state.id = None
            new_state.bi_id = None
            new_state.save()
            smap[state.id] = new_state
        # Clone transitions
        for transition in Transition.objects.filter(workflow=wf.id):
            new_transition = deepcopy(transition)
            new_transition.workflow = new_wf
            new_transition.from_state = smap[transition.from_state.id]
            new_transition.to_state = smap[transition.to_state.id]
            new_transition.id = None
            new_transition.bi_id = None
            new_transition.save()
        #
        return {"id": str(new_wf.id)}
