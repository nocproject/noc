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
from noc.fm.models.dispositionrule import DispositionRule
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.interactionlog import Interaction, InteractionLog

logger = logging.getLogger(__name__)


class EventAction(enum.Enum):
    DROP = 1
    LOG = 2
    DISPOSITION = 3

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class ActionSet(object):

    def __init__(self):
        self.actions: Dict[str, List[Tuple[Callable, Optional[Callable]]]] = {}
        self.add_handlers: int = 0
        self.add_notifications: int = 0

    def iter_actions(self, event_class: str, ctx: Dict[str, Any]) -> Iterable[Callable]:
        """"""
        if event_class not in self.actions:
            return
        for a, match in self.actions[event_class]:
            if match and not match(ctx):
                continue
            yield a

    def update_rule(self, data):
        """Update rule from lookup"""

    def delete_rule(self, rid: str):
        """Remove rule from lookup"""

    def load(self, skip_load_rules: bool = False):
        """
        Load rules from database
        """
        actions = defaultdict(list)
        logger.info("Load Disposition Rule")
        for rule in DispositionRule.objects.filter(is_active=True).order_by("preference"):
            m = rule.get_matcher()
            for ec in rule.get_event_classes():
                for h in rule.handlers or []:
                    try:
                        actions[ec.id] += [(h.handler.get_handler(), m)]
                    except ImportError:
                        logger.error("Failed to load handler '%s'. Ignoring", h)
                    self.add_handlers += 1
                if rule.notification_group:
                    actions[ec.id] += [
                        partial(
                            self.send_notification,
                            notification_group=str(rule.notification_group.id),
                        ),
                    ]
                if rule.object_actions and rule.object_actions.interaction_audit:
                    actions[ec.id] += [
                        partial(
                            self.interaction_audit,
                            interaction=rule.object_actions.interaction_audit,
                        ),
                    ]
                    self.add_handlers += 1
                if rule.object_actions and rule.object_actions.run_discovery:
                    actions[ec.id] += [
                        partial(
                            self.run_discovery, interaction=rule.object_actions.interaction_audit
                        ),
                    ]
                    self.add_handlers += 1
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
