# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# wf.workflow application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State
from noc.wf.models.transition import Transition, TransitionVertex
from noc.core.translation import ugettext as _
from noc.sa.interfaces.base import (
    StringParameter, IntParameter, DictListParameter, BooleanParameter,
    StringListParameter, NoneParameter
)


class WorkflowApplication(ExtDocApplication):
    """
    Workflow application
    """
    title = _("Workflows")
    menu = [_("Setup"), _("Workflow")]
    model = Workflow

    @view("^(?P<id>[0-9a-f]{24})/config/",
          method=["GET"], access="write", api=True)
    def api_get_config(self, request, id):
        wf = self.get_object_or_404(Workflow, id)
        r = {
            "id": str(wf.id),
            "name": wf.name,
            "is_active": wf.is_active,
            "description": wf.description,
            "states": [],
            "transitions": []
        }
        for state in State.objects.filter(workflow=wf.id):
            sr = {
                "id": str(state.id),
                "name": state.name,
                "description": state.description,
                "is_default": state.is_default,
                "is_productive": state.is_productive,
                "update_last_seen": state.update_last_seen,
                "ttl": state.ttl,
                "update_expired": state.update_expired,
                "on_enter_handlers": state.on_enter_handlers,
                "job_handler": state.job_handler,
                "on_leave_handlers": state.on_leave_handlers,
                "bi_id": str(state.bi_id) if state.bi_id else None,
                "x": state.x,
                "y": state.y
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
                "vertices": [{"x": v.x, "y": v.y} for v in t.vertices],
                "bi_id": str(t.bi_id) if t.bi_id else None,
            }
            r["transitions"] += [tr]
        return r

    @view("^(?P<id>[0-9a-f]{24})/config/",
          method=["POST"], access="write", api=True,
          validate={
              "name": StringParameter(),
              "description": StringParameter(default=""),
              "is_active": BooleanParameter(default=False),
              "states": DictListParameter(attrs={
                  "id": StringParameter(default=""),
                  "name": StringParameter(),
                  "description": StringParameter(default=""),
                  "is_default": BooleanParameter(default=False),
                  "is_productive": BooleanParameter(default=False),
                  "update_last_seen": BooleanParameter(default=False),
                  "ttl": IntParameter(default=0),
                  "update_expired": BooleanParameter(default=False),
                  "on_enter_handlers": StringListParameter(),
                  "job_handler": NoneParameter() or StringParameter(),
                  "on_leave_handlers": StringListParameter(),
                  "x": IntParameter(),
                  "y": IntParameter()

              }),
              "transitions": DictListParameter(attrs={
                  "id": StringParameter(default=""),
                  "from_state": StringParameter(),
                  "to_state": StringParameter(),
                  "is_active": BooleanParameter(default=False),
                  "event": StringParameter(),
                  "label": StringParameter(),
                  "description": StringParameter(default=""),
                  "enable_manual": BooleanParameter(),
                  "handlers": StringListParameter(),
                  "vertices": DictListParameter(attrs={
                      "x": IntParameter(),
                      "y": IntParameter()
                  })
              })
          }
          )
    def api_save_config(self, request, id, name, description, states, transitions, **kwargs):
        wf = self.get_object_or_404(Workflow, id)
        # Update workflow
        wf.name = name
        wf.description = description
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
            # Update state attributes
            if not state:
                state = State()
                changed = True
            else:
                changed = False
            print "State: %s" % s["name"]
            for k in s:
                if k in ("id", "bi_id"):
                    continue
                if getattr(state, k) != s[k]:
                    print "  %s: %r -> %r" % (k, getattr(state, k), s[k])
                    setattr(state, k, s[k])
                    changed = True
            if changed:
                print "  ... Saving"
                state.save()
            state_names[state.name] = state
        # Delete hanging state
        for sid in set(current_states) - seen_states:
            self.delete_state(current_states[sid])
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
            print "Transition: %s --> %s" % (t["from_state"], t["to_state"])
            for k in t:
                if k in ("id", "bi_id"):
                    continue
                elif k in ("from_state", "to_state"):
                    t[k] = state_names[t[k]]
                elif k == "vertices":
                    t[k] = [TransitionVertex(x=vx["x"], y=vx["y"]) for vx in t[k]]
                old = getattr(transition, k)
                if old != t[k]:
                    print "  %s: %r -> %r" % (k, old, t[k])
                    setattr(transition, k, t[k])
                    changed = True
            if changed:
                print "  ... Saving"
                transition.save()
        # Delete hanging transitions
        for tid in set(current_transitions) - seen_transitions:
            print "Delete %s" % tid
            # current_transitions[tid].delete()

    def delete_state(self, state):
        """
        Delete state
        :param state:
        :return:
        """
        print "Delete state: %s" % state.name
