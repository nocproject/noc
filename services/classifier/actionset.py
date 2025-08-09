# ----------------------------------------------------------------------
#  ActionSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from collections import defaultdict
from functools import partial
from typing import Dict, Tuple, Optional, Callable, List, Any, Iterable

# NOC modules
from noc.core.fm.event import Event
from noc.core.fm.enum import EventAction, EventSeverity
from noc.core.debug import error_report
from noc.core.mx import send_message, MessageType, MX_NOTIFICATION_GROUP_ID
from noc.core.matcher import build_matcher
from noc.core.handler import get_handler
from noc.fm.models.dispositionrule import DispositionRule
from noc.sa.models.managedobject import ManagedObject
from noc.services.classifier.eventconfig import EventConfig
from noc.services.datastream.models.cfgevent import Rule

action_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Action:
    name: str
    stop_processing: bool = False
    match: Optional[Callable] = None
    event_match: Optional[Callable] = None
    event: Tuple[Callable, ...] = None
    target: Tuple[Callable, ...] = None
    resource: Dict[str, Tuple[Callable, ...]] = None
    action: EventAction.LOG = EventAction.LOG


class ActionSet(object):

    def __init__(self, logger=None):
        # EventClass
        self.logger = logger or action_logger
        self.actions: Dict[str, List[Action]] = {}
        self.add_handlers: int = 0
        self.add_event_actions: int = 0
        self.add_target_actions: int = 0
        self.add_notifications: int = 0
        self.default_resource_action = EventAction.LOG

    def iter_actions(
        self,
        event_class: str,
        ctx: Dict[str, Any],
        e_vars: Dict[str, Any],
    ) -> Iterable[Callable]:
        """"""
        if event_class not in self.actions:
            return
        self.logger.debug(
            "[|%s] Processed action: %s/%s", event_class, self.actions[event_class], e_vars
        )
        for a in self.actions[event_class]:
            if a.match and not a.match(ctx):
                continue
            if a.event_match and not a.event_match(e_vars):
                continue
            yield from a.event or []
            yield from a.target or []
            yield from a.resource.values()
            if a.stop_processing:
                break

    def update_rule(self, rid: str, data):
        """Update rule from lookup"""
        actions = []
        for d in data:
            actions += self.from_config(d)
        if rid not in self.actions:
            self.add_event_actions += 1
        else:
            self.logger.info("[%s] Update event actions: %s", rid, actions)
        self.actions[rid] = actions

    def delete_rule(self, rid: str):
        """Remove rule from lookup"""
        if rid in self.actions:
            del self.actions[rid]

    def from_config(self, data: Dict[str, Any]) -> List[Action]:
        """Create actions"""
        rule = Rule.model_validate(data)
        event_actions = []
        for h in rule.handlers or []:
            try:
                event_actions += [partial(self.run_handler, handler=get_handler(h))]
            except ImportError:
                self.logger.error("Failed to load handler '%s'. Ignoring", h)
            self.add_handlers += 1
        target_actions, resource_actions = [], defaultdict(list)
        if rule.notification_group:
            target_actions += [
                partial(
                    self.send_notification,
                    notification_group=str(rule.notification_group),
                )
            ]
            self.add_notifications += 1
        if rule.target:
            for a in rule.target.actions or []:
                args = a.args or {}
                h = a.action.from_config(a.key, **args)
                if h:
                    target_actions.append(h)
        if rule.action == EventAction.DISPOSITION:
            event_actions += [
                partial(
                    self.dispose_event, ignore_target=data.get("ignore_target_on_dispose", False)
                )
            ]
        elif rule.action == EventAction.DROP:
            event_actions += [self.drop_event]
        elif rule.action == EventAction.DROP_MX:
            event_actions += [self.drop_mx_event]
        for r in rule.resources or []:
            for a in r.actions:
                args = a.args or {}
                resource_actions[r.model].append(a.action.from_config(key=a.key, **args))
        return [
            Action(
                name=data["name"],
                match=build_matcher(data["match_expr"]) if data["match_expr"] else None,
                event_match=(
                    build_matcher(data["vars_match_expr"]) if data.get("vars_match_expr") else None
                ),
                event=tuple(event_actions),
                target=tuple(target_actions),
                resource={k: tuple(v) for k, v in resource_actions},
                stop_processing=data["stop_processing"],
            )
        ]

    def load(self, skip_load_rules: bool = False):
        """
        Load rules from database
        """
        actions = defaultdict(list)
        self.logger.info("Load Disposition Rule")
        for rule in DispositionRule.objects.filter(is_active=True).order_by("preference"):
            for ec in rule.get_event_classes():
                actions[str(ec.id)] += self.from_config(DispositionRule.get_rule_config(rule))
        self.actions = actions
        self.logger.info("Handlers are loaded: %s", self.add_handlers)

    def run_actions(
        self,
        event: Event,
        target: ManagedObject,
        resources: List[Any],
        config: EventConfig,
        categories=None,
    ) -> EventAction:
        """Processed actions on Event"""
        ctx = {
            "labels": frozenset(event.labels or []),
            "service_groups": frozenset(target.effective_service_groups or []) if target else [],
            "remote_system": event.remote_system,
        }
        action = None
        # Event and Target action
        for a in self.iter_actions(config.event_class_id, ctx, event.vars):
            r = a(event, target, resources)
            if r == EventAction.DROP:
                return r
            elif r and r != EventAction.LOG:
                action = EventAction.DISPOSITION
        return action

    @staticmethod
    def run_resources_action(
        event: Event,
        managed_object: ManagedObject,
        resources: List[Any],
        handler: Callable,
    ) -> EventAction:
        """"""
        action = EventAction.LOG
        for res in resources:
            r = handler(event, res)
            if r and r == EventAction.DROP:
                return r
        return action

    @staticmethod
    def run_handler(
        event: Event,
        managed_object: ManagedObject,
        resources: List[Any],
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
        resources: List[Any],
        notification_group: Optional[str] = None,
    ):
        """Send Event Notification"""
        action_logger.debug("Sending status change notification")
        headers = managed_object.get_mx_message_headers(event.labels)
        headers[MX_NOTIFICATION_GROUP_ID] = str(notification_group).encode()
        msg = event.get_message_context(managed_object)
        send_message(
            data=msg,
            message_type=MessageType.EVENT,
            headers=headers,
        )

    @staticmethod
    def drop_event(
        event: Event,
        managed_object: ManagedObject,
        resources: List[Any],
    ):
        """"""
        return EventAction.DROP

    @staticmethod
    def drop_mx_event(
        event: Event,
        managed_object: ManagedObject,
        resources: List[Any],
    ):
        """"""
        return EventAction.DROP_MX

    @staticmethod
    def dispose_event(
        event: Event,
        managed_object: ManagedObject,
        resources: List[Any],
        ignore_target: bool = False,
    ):
        """"""
        if managed_object:
            return EventAction.DISPOSITION
        elif not managed_object and ignore_target:
            return EventAction.DISPOSITION
        return EventAction.LOG

    def get_resource_action(
        self,
        event: Event,
        resource: Any,
    ):
        """"""
        action = resource.profile.link_events
        if action == "I":
            # Ignore
            if resource:
                self.logger.info(
                    "[%s|%s|%s] Marked as ignored by interface profile '%s' (%s)",
                    event.id,
                    resource.managed_object.name,
                    resource.managed_object.address,
                    resource.profile.name,
                    resource,
                )
            else:
                self.logger.info(
                    "[%s|%s|%s] Marked as ignored by default interface profile",
                    event.id,
                    resource.managed_object.name,
                    resource.managed_object.address,
                )
            return EventAction.DROP
        elif action == "L":
            # Do not dispose
            if resource:
                self.logger.info(
                    "[%s|%s|%s] Marked as not disposable by interface profile '%s' (%s)",
                    event.id,
                    resource.managed_object.name,
                    resource.managed_object.address,
                    resource.profile.name,
                    resource.name,
                )
            else:
                self.logger.info(
                    "[%s|%s|%s] Marked as not disposable by default interface",
                    event.id,
                    resource.managed_object.name,
                    resource.managed_object.address,
                )
            event.type.severity = EventSeverity.IGNORED  # do_not_dispose
        return self.default_resource_action
