# ----------------------------------------------------------------------
#  ActionSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import enum
import datetime
from collections import defaultdict
from functools import partial
from typing import Dict, Tuple, Optional, Callable, List, Any, Iterable

# NOC modules
from noc.core.fm.event import Event
from noc.core.debug import error_report
from noc.core.mx import send_message, MessageType, MX_NOTIFICATION_GROUP_ID
from noc.core.matcher import build_matcher
from noc.core.handler import get_handler
from noc.fm.models.dispositionrule import DispositionRule
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.interactionlog import Interaction, InteractionLog

logger = logging.getLogger(__name__)


class EventAction(enum.Enum):
    """Event Action.
    * Drop - do not save
    * Ignored - do not disposition
    * Log - Save only
    * Disposition - Create Alarm
    """

    DROP = 1
    LOG = 2
    DISPOSITION = 3

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class ActionSet(object):

    def __init__(self):
        # EventClass
        self.actions: Dict[str, List[Tuple[Callable, Optional[Callable]]]] = {}
        self.add_handlers: int = 0
        self.add_actions: int = 0
        self.add_notifications: int = 0

    def iter_actions(self, event_class: str, ctx: Dict[str, Any]) -> Iterable[Callable]:
        """"""
        if event_class not in self.actions:
            return
        for a, match in self.actions[event_class]:
            if match and not match(ctx):
                continue
            yield a

    def update_rule(self, rid: str, data):
        """Update rule from lookup"""
        actions = []
        for d in data:
            actions += self.from_config(d)
        if rid not in self.actions:
            self.add_actions += 1
        else:
            logger.info("[%s] Update event actions: %s", rid, actions)
        self.actions[rid] = actions

    def delete_rule(self, rid: str):
        """Remove rule from lookup"""
        if rid in self.actions:
            del self.actions[rid]

    def from_config(self, data: Dict[str, Any]) -> List[Tuple[Callable, Optional[Callable]]]:
        """Create actions"""
        r = []
        if data["match_expr"]:
            m = build_matcher(data["match_expr"])
        else:
            m = None
        for h in data.get("handlers") or []:
            try:
                r += [(get_handler(h), m)]
            except ImportError:
                logger.error("Failed to load handler '%s'. Ignoring", h)
            self.add_handlers += 1
        if "notification_group" in data:
            r += [
                (
                    partial(
                        self.send_notification,
                        notification_group=str(data["notification_group"]),
                    ),
                    m,
                )
            ]
            self.add_notifications += 1
        if "object_actions" in data and data["object_actions"]["interaction_audit"]:
            r += [
                (
                    partial(
                        self.interaction_audit,
                        interaction=data["object_actions"]["interaction_audit"],
                    ),
                    m,
                )
            ]
            self.add_handlers += 1
        if "object_actions" in data and data["object_actions"]["run_discovery"]:
            r += [
                (
                    partial(
                        self.run_discovery,
                        interaction=data["object_actions"]["interaction_audit"],
                    ),
                    m,
                )
            ]
            self.add_handlers += 1
        if "action" in data and data["action"] == 3:
            r += [(lambda event, mo: EventAction.DISPOSITION, None)]
        return r

    def load(self, skip_load_rules: bool = False):
        """
        Load rules from database
        """
        actions = defaultdict(list)
        logger.info("Load Disposition Rule")
        for rule in DispositionRule.objects.filter(is_active=True).order_by("preference"):
            for ec in rule.get_event_classes():
                actions[str(ec.id)] += self.from_config(DispositionRule.get_rule_config(rule))
        self.actions = actions
        logger.info("Handlers are loaded: %s", self.add_handlers)

    @staticmethod
    def run_handler(
        event: Event,
        managed_object: ManagedObject,
        handler: Callable,
    ):
        """Run Event Handlers"""
        try:
            handler(event, managed_object)
        except Exception:
            error_report()

    @staticmethod
    def send_notification(
        event: Event,
        managed_object: ManagedObject,
        notification_group: Optional[str] = None,
    ):
        """Send Event Notification"""
        logger.debug("Sending status change notification")
        headers = managed_object.get_mx_message_headers(event.labels)
        headers[MX_NOTIFICATION_GROUP_ID] = str(notification_group).encode()
        msg = event.get_message_context(managed_object)
        send_message(
            data=msg,
            message_type=MessageType.EVENT,
            headers=headers,
        )

    @staticmethod
    def run_action(
        event: Event,
        managed_object: ManagedObject,
        action: Optional[str] = None,
    ):
        """"""

    @staticmethod
    def run_discovery(
        event: Event,
        managed_object: ManagedObject,
        interaction: Interaction,
    ):
        """Run Discovery"""
        if (
            interaction == Interaction.OP_STARTED
            and managed_object.object_profile.box_discovery_on_system_start
        ):
            managed_object.run_discovery(
                delta=managed_object.object_profile.box_discovery_system_start_delay
            )
        elif (
            interaction == Interaction.OP_CONFIG_CHANGED
            and managed_object.object_profile.box_discovery_on_config_changed
        ):
            managed_object.run_discovery(
                delta=managed_object.object_profile.box_discovery_config_changed_delay
            )

    @staticmethod
    def interaction_audit(
        event: Event,
        managed_object: ManagedObject,
        interaction: Interaction,
    ):
        """Audit interaction"""
        if interaction == Interaction.OP_COMMAND:
            text = event.vars.get("command")
        else:
            text = interaction.config.text
        InteractionLog(
            timestamp=event.timestamp,
            expire=event.timestamp + datetime.timedelta(seconds=interaction.config.ttl),
            object=managed_object.id,
            user=event.vars.get("user"),
            op=interaction,
            text=text,
        ).save()
