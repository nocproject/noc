# ----------------------------------------------------------------------
# Actions applied to model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from functools import partial
from typing import Callable, Optional, Any, Dict

# NOC Modules
from noc.core.diagnostic.types import DiagnosticState
from noc.core.defer import call_later
from noc.core.handler import get_handler
from noc.core.models.cfginteractions import Interaction
from noc.models import get_model_id
from noc.config import config

MIN_DISCOVERY_DELAY_SEC = 60


class ActionType(enum.Enum):
    """
    Actions applied to model instances if supported
    Attributes:
        ACTION_COMMAND: Run command on ManagedObject (if profile supported)
        AUDIT_COMMAND: Log execute command to audit
        RUN_DISCOVERY: Run discovery
        FIRE_WF_EVENT: Fire workflow event, if Workflow API supported
        SET_OPER_STATE: Update Operation State on Resource
        UP_DOWN_DIAGNOSTIC: Send Diagnostic UP/DOWN event
        HANDLER: Custom handler for execute

    """

    ACTION_COMMAND = "action_command"
    AUDIT_COMMAND = "audit_command"
    RUN_DISCOVERY = "run_discovery"
    FIRE_WF_EVENT = "fire_wf_event"
    FIRE_OBJ_EVENT = "fire_obj_event"
    SET_OPER_STATE = "set_oper_state"
    UP_DOWN_DIAGNOSTIC = "update_diagnostic"
    HANDLER = "handler"

    def is_supported(self, obj) -> bool:
        match self:
            case self.ACTION_COMMAND:
                return hasattr(obj, "actions")
            case self.AUDIT_COMMAND:
                return get_model_id(obj) == "sa.ManagedObject"
            case self.RUN_DISCOVERY:
                return hasattr(obj, "run_discovery")
            case self.FIRE_WF_EVENT:
                return getattr(obj, "_has_workflow", False)
            case self.SET_OPER_STATE:
                return hasattr(obj, "set_oper_status")
            case self.UP_DOWN_DIAGNOSTIC:
                return hasattr(obj, "diagnostic")
            case self.FIRE_OBJ_EVENT:
                return hasattr(obj, "event")
            case self.HANDLER:
                return True
        return False

    def run_action(
        self,
        obj: Any,
        key: str,
        cfg: Dict[str, Any],
        immediate: bool = True,
        **kwargs,
    ):
        if not immediate:
            # job = self.get_job(obj, key, **cfg, **kwargs)
            # worker or runner
            return
        h = self.from_config(key, **cfg)
        if not h:
            return
        try:
            h(obj, **kwargs)
        except Exception:
            pass

    def from_config(self, key: str, **kwargs) -> Optional[Callable]:
        """Callable for execute action"""
        match self:
            case self.ACTION_COMMAND:
                return partial(self.run_action_command, action_name=key)
            case self.AUDIT_COMMAND:
                return partial(self.interaction_audit, audit=int(key))
            case self.RUN_DISCOVERY:
                return partial(self.run_discovery, **kwargs)
            case self.FIRE_WF_EVENT:
                return partial(self.send_workflow_event, **kwargs)
            case self.SET_OPER_STATE:
                return partial(self.set_oper_status, **kwargs)
            case self.UP_DOWN_DIAGNOSTIC:
                return partial(self.diagnostic_up_down, **kwargs)
            case self.FIRE_OBJ_EVENT:
                return partial(self.send_obj_event, **kwargs)
            case self.HANDLER:
                return get_handler(key)
        return None

    @staticmethod
    def send_workflow_event(obj, wf_event: str, **kwargs):
        """Send Workflow signal"""
        obj.fire_event(wf_event)

    @staticmethod
    def send_obj_event(obj, **kwargs):
        """Send Workflow signal"""
        obj.event(**kwargs)

    @staticmethod
    def set_oper_status(obj, status, ts: Optional[datetime.datetime] = None, **kwargs):
        """"""
        obj.set_oper_status(status=status, timestamp=ts)

    @staticmethod
    def diagnostic_up_down(
        obj,
        diagnostic: str,
        status: bool,
        ts: Optional[datetime.datetime] = None,
        reason: Optional[str] = None,
        **kwargs,
    ):
        """UP/Down Diagnostic"""
        if status:
            state = DiagnosticState.enabled
        else:
            state = DiagnosticState.failed
        reason = reason or "From automate action"
        obj.diagnostic.set_state(
            diagnostic=diagnostic,
            state=state,
            reason=reason,
            changed_ts=ts,
        )

    @staticmethod
    def run_discovery(
        obj,
        delay: Optional[int] = None,
        check: Optional[str] = None,
        audit: Optional[int] = None,
        **kwargs,
    ):
        """Run ManagedObject discovery"""
        if audit:
            audit = Interaction(int(audit))
        if audit == Interaction.OP_REBOOT and not obj.object_profile.box_discovery_on_system_start:
            return
        if audit == Interaction.OP_REBOOT:
            delay = obj.object_profile.box_discovery_system_start_delay
        elif (
            audit == Interaction.OP_CONFIG_CHANGED
            and not obj.object_profile.box_discovery_on_config_changed
        ):
            return
        elif audit == Interaction.OP_CONFIG_CHANGED:
            delay = obj.object_profile.box_discovery_config_changed_delay
        else:
            delay = max(delay or config.correlator.discovery_delay, MIN_DISCOVERY_DELAY_SEC)
        if check:
            call_later(
                obj.id,
                job_class=obj.BOX_DISCOVERY_JOB,
                _checks=[check],
                max_runs=1,
                delay=delay,
            )

            return
        obj.run_discovery(delta=delay)

    @staticmethod
    def run_action_command(
        obj,
        action_name: str,
        **kwargs,
    ):
        """Run Action Command on ManagedObject Action Proxy"""
        # Map vars
        scr = getattr(obj.actions, action_name)
        scr(**kwargs)

    @staticmethod
    def interaction_audit(
        obj,
        audit: int,
        ts: Optional[datetime.datetime] = None,
        command: Optional[str] = None,
        user: Optional[str] = None,
        **kwargs,
    ):
        """Audit interaction"""
        from noc.sa.models.interactionlog import InteractionLog

        interaction = Interaction(int(audit))
        if interaction == Interaction.OP_COMMAND:
            text = command
        else:
            text = interaction.config.text
        InteractionLog(
            timestamp=ts,
            expire=ts + datetime.timedelta(seconds=interaction.config.ttl),
            object=obj.id,
            user=user,
            op=interaction,
            text=text,
        ).save()
