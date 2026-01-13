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

# Third-party modules
from pydantic import ValidationError

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
from noc.models import get_model_id

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
    action: EventAction = EventAction.LOG

    def iter_event_actions(self) -> Iterable[Callable]:
        """Iter event action"""
        # First Event Handler
        for h in self.event:
            yield h

    def iter_target_actions(self) -> Iterable[Callable]:
        """Iter Target action"""
        for h in self.target:
            yield h

    def iter_resource_actions(self, resource: Any) -> Iterable[Callable]:
        """Iterate over resource action"""
        if not self.resource:
            return
        mid = get_model_id(resource)
        for h in self.resource.get(mid, []):
            yield h


class ActionSet(object):
    def __init__(self, logger=None):
        # EventClass
        # Abduct Detector
        self.logger = logger or action_logger
        self.actions: Dict[str, List[Action]] = {}
        self.add_handlers: int = 0
        self.add_event_actions: int = 0
        self.add_target_actions: int = 0
        self.add_notifications: int = 0

    def iter_actions(
        self,
        event_class: str,
        ctx: Dict[str, Any],
        e_vars: Dict[str, Any],
    ) -> Iterable[Action]:
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
            yield a
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
        try:
            rule = Rule.model_validate(data)
        except ValidationError as e:
            self.logger.error("[%s] Failed load action rule: %s", data["name"], e)
            return []
        event_actions = []
        for h in rule.handlers or []:
            try:
                event_actions += [partial(self.run_event_handler, handler=get_handler(h))]
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
        for a in rule.actions or []:
            args = a.args or {}
            h = a.action.from_config(a.key, **args)
            if not h:
                continue
            if a.is_target:
                target_actions.append(h)
            else:
                # Resource action
                resource_actions[a.model_id].append(h)
        return [
            Action(
                name=data["name"],
                match=build_matcher(data["match_expr"]) if data["match_expr"] else None,
                event_match=(
                    build_matcher(data["vars_match_expr"]) if data.get("vars_match_expr") else None
                ),
                event=tuple(event_actions),
                target=tuple(target_actions),
                resource={k: tuple(v) for k, v in resource_actions.items()},
                stop_processing=data["stop_processing"],
                action=rule.action,
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
                actions[str(ec.id)] += self.from_config(DispositionRule.get_event_rule_config(rule))
        self.actions = actions
        self.logger.info("Handlers are loaded: %s", self.add_handlers)

    def run_actions(
        self,
        event: Event,
        target: ManagedObject,
        resources: List[Any],
        config: EventConfig,
    ) -> Tuple[EventAction, int]:
        """
        Processed actions on Event
        Args:
            event: Event instance
            target: Object
            resources: Resources resolved from event
            config: EventConfig
        """
        ctx = {
            "labels": frozenset(event.labels or []),
            "service_groups": frozenset(target.effective_service_groups or []) if target else [],
            "remote_system": event.remote_system,
        }
        drop_action: Optional[EventAction] = None
        to_dispose = False
        resource_action = None
        num = 0
        for a in self.iter_actions(config.event_class_id, ctx, event.vars):
            r = a.action
            # Event Handlers
            for h in a.iter_event_actions():
                try:
                    r = h(event, target) or r
                except Exception as e:
                    self.logger.error(
                        "[%s|%s] Error when execute event: %s", event.id, a.name, str(e)
                    )
            # Target Handlers
            for h in a.iter_target_actions():
                try:
                    h(target, event=event, ts=event.timestamp, **event.vars)
                except Exception as e:
                    self.logger.error(
                        "[%s|%s] Error when execute Target Action: %s", event.id, a.name, str(e)
                    )
            # Resource Handlers
            for instance in resources or []:
                for h in a.iter_resource_actions(instance):
                    try:
                        h(instance, event=event, ts=event.timestamp, **event.vars)
                    except Exception as e:
                        self.logger.error(
                            "[%s|%s] Error when execute Resource Action: %s",
                            event.id,
                            a.name,
                            str(e),
                        )
                # Replace to interface method
                # Default Link Event
                if (
                    config.is_link_event
                    and not resource_action
                    and hasattr(instance, "as_resource")
                    and instance.as_resource().startswith("if:")
                ):
                    # "inv.Interface"
                    resource_action = self.get_resource_action(instance, event=event)
            if r.to_dispose:
                to_dispose |= True
            elif r.is_drop and not drop_action:
                drop_action = r
            self.logger.debug("[%s] Processed action. Resolution: %s", a.name, r)
            num += 1
        # Resource Action
        if resource_action:
            return resource_action, num
        # Preferred Disposition
        if to_dispose:
            return EventAction.DISPOSITION, num
        if drop_action:
            return drop_action, num
        # Log - default Action
        return EventAction.LOG, num

    @staticmethod
    def run_event_handler(
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
    def run_resource_handler(
        event: Event,
        resource: Any,
        handler: Callable,
        **kwargs,
    ):
        """Run Event Handlers"""
        try:
            handler(resource, event=event)
        except Exception:
            error_report()

    @staticmethod
    def send_notification(
        managed_object: ManagedObject,
        event: Event,
        notification_group: Optional[str] = None,
        **kwargs,
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

    def get_resource_action(
        self,
        resource: Any,
        event: Event,
        **kwargs,
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
        if action == "L":
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
        return None
