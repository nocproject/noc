# ----------------------------------------------------------------------
#  ActionSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import enum
from collections import defaultdict
from functools import partial
from typing import Dict, Tuple, Optional, Callable, List, Any, Iterable

# NOC modules
from noc.core.fm.event import Event
from noc.core.handler import get_handler
from noc.core.debug import error_report
from noc.core.mx import MessageType
from noc.fm.models.dispositionrule import DispositionRule
from noc.fm.models.eventclass import EventClass
from noc.sa.models.managedobject import ManagedObject

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
        logger.info("Load Handler")
        processed = set()
        actions = defaultdict(list)
        for ec in EventClass.objects.filter():
            handlers = ec.handlers or []
            if not handlers:
                continue
            logger.debug("    <%s>: %s", ec.name, ", ".join(handlers))
            for h in handlers:
                if h in processed:
                    continue
                processed.add((ec.id, h))
                try:
                    h = get_handler(h)
                except ImportError:
                    logger.error("Failed to load handler '%s'. Ignoring", h)
                actions[ec.id] += [(partial(self.run_handler, handler=h), None)]
                self.add_handlers += 1
        logger.info("Load Disposition Rule")
        for rule in DispositionRule.objects.filter(is_active=True):
            rule: DispositionRule
            for ec in rule.get_event_classes():
                for h in rule.handlers or []:
                    if (ec.id, h.handler.handler) in processed:
                        continue
                    try:
                        actions[ec.id] += [(h.handler.get_handler(), rule.get_matcher())]
                    except ImportError:
                        logger.error("Failed to load handler '%s'. Ignoring", h)
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
        managed_object.event(MessageType.EVENT.value, event.get_message_context())

    @staticmethod
    def run_action(
        event: Event,
        managed_object: ManagedObject,
        action: Optional[str] = None,
    ):
        """"""
