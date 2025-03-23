# ----------------------------------------------------------------------
#  RuleSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from itertools import chain
from collections import defaultdict
from typing import Dict, Any, Tuple, Optional, Callable

# NOC modules
from .rule import Rule
from .exception import InvalidPatternException, EventProcessingFailed
from .rulelookup import RuleLookup
from noc.config import config
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.fm.models.enumeration import Enumeration
from noc.sa.models.profile import GENERIC_PROFILE
from noc.core.handler import get_handler
from noc.core.profile.loader import loader as profile_loader
from noc.core.perf import metrics
from noc.core.fm.event import Event
from noc.core.fm.enum import EventSource
from noc.sa.interfaces.base import (
    IPv4Parameter,
    IPv6Parameter,
    IPParameter,
    IPv4PrefixParameter,
    IPv6PrefixParameter,
    PrefixParameter,
    MACAddressParameter,
    InterfaceTypeError,
)

logger = logging.getLogger(__name__)


class RuleSet(object):

    def __init__(self):
        self.rules: Dict[Tuple[Optional[str], str], RuleLookup] = (
            {}
        )  # (profile, chain) -> [rule, ..., rule]
        self.enumerations: Dict[str, Dict[str, str]] = {}  # name -> value -> enumerated
        self.lookup_cls: Optional[Callable] = None
        self.default_rule: Optional[Rule] = None
        #
        # is_failed: bool = False
        # metric block
        self.add_rules: int = 0
        # processed: int = 0

    def update_rule(self, data):
        """Update rule from lookup"""
        rule = Rule.from_config(data, self.enumerations)
        changed = False
        for rl in self.rules.values():
            changed |= rl.update_rule(rule)
        if changed:
            logger.info("[%s|%s] Rule updated", rule.id, rule.name)
            return changed
        # Add New Rule
        if not rule.profiles:
            keys = [(GENERIC_PROFILE, rule.source.value)]
        else:
            keys = [(p, rule.source.value) for p in rule.profiles]
        for key in keys:
            if key not in self.rules:
                self.rules[key] = self.lookup_cls([rule])
            else:
                self.rules[key].add_rule(rule)
            self.add_rules += 1

    def delete_rule(self, rid: str):
        """Remove rule from lookup"""
        rule = None
        for rl in self.rules.values():
            rule = rl.delete_rule(rid)
        if rule:
            logger.info("[%s] Rule removed: %s", rule.id, rule.name)
        else:
            logger.info("[%s] Rule with id not found", rid)

    def load(self, skip_load_rules: bool = False):
        """
        Load rules from database
        """
        self.lookup_cls = get_handler(config.classifier.lookup_handler)
        self.rules = {}
        logger.info("Loading rules")
        n = 0
        rules = defaultdict(list)
        self.default_rule = EventClassificationRule.objects.filter(
            name=config.classifier.default_rule
        ).first()
        if self.default_rule:
            self.default_rule = Rule.from_config(
                EventClassificationRule.get_rule_config(self.default_rule),
                self.enumerations,
            )
        #
        self.load_enumerations()
        if skip_load_rules:
            return
        # Initialize rules
        for r in EventClassificationRule.objects.order_by("preference"):
            try:
                rule = Rule.from_config(
                    EventClassificationRule.get_rule_config(r),
                    self.enumerations,
                )
            except InvalidPatternException as e:
                logger.error("Failed to load rule '%s': Invalid patterns: %s", r.name, e)
                continue
            # Find profile restrictions
            if not rule.profiles:
                rules[GENERIC_PROFILE, rule.source.value] += [rule]
                continue
            # Apply rules to appropriative chains
            for p in rule.profiles:
                rules[p, rule.source.value] += [rule]
            n += 1
        # Apply lookup solution
        self.rules = {k: self.lookup_cls(rules[k]) for k in rules}
        logger.info("%d rules are loaded in the %d chains", n, len(self.rules))

    def load_enumerations(self):
        logger.info("Loading enumerations")
        n = 0
        # self.enumerations = {}
        for e in Enumeration.objects.all():
            r = {}
            for k, v in e.values.items():
                for vv in v:
                    r[vv.lower()] = k
            self.enumerations[e.name] = r
            n += 1
        logger.info("%d enumerations loaded" % n)

    def find_rule(
        self,
        event: Event,
        vars: Dict[str, Any],
    ) -> Tuple[Optional[Rule], Optional[Dict[str, Any]]]:
        """
        Find first matching classification rule

        Args:
            event: Event
            vars: raw and resolved variables
        Returns: Event class and extracted variables
        """
        # Get chain
        if event.type.source == EventSource.SYSLOG and not event.message:
            return None, None
        # Find rules lookup
        lookup = self.rules.get((event.type.profile, event.type.source.value))
        if lookup:
            lookup = lookup.lookup_rules(event, vars)
        gen_lookup = self.rules.get((GENERIC_PROFILE, event.type.source.value))
        if gen_lookup:
            gen_lookup = gen_lookup.lookup_rules(event, vars)
        for r in chain.from_iterable([lookup or [], gen_lookup or []]):
            # Try to match rule
            metrics["rules_checked"] += 1
            v = r.match(event.message, vars, event.labels)
            if v is not None:
                logger.debug(
                    "[%s] Matching class for event %s found: %s (Rule: %s)",
                    event.target.name,
                    event.id,
                    r.event_class_name,
                    r.name,
                )
                return r, v
        if self.default_rule:
            return self.default_rule, {}
        return None, None

    def eval_vars(self, event: Event, event_class, r_vars: Dict[str, Any]):
        """Evaluate rule variables"""
        r = {}
        # Resolve e_vars
        for ecv in event_class.vars:
            # Check variable is present
            if ecv.name not in r_vars:
                if ecv.required:
                    raise Exception("Required variable '%s' is not found" % ecv.name)
                continue
            # Decode variable
            v = r_vars[ecv.name]
            decoder = getattr(RuleSet, f"decode_{ecv.type}", None)
            # resolve_ interface, instance
            if decoder:
                try:
                    v = decoder(event, v)
                except InterfaceTypeError:
                    raise EventProcessingFailed(
                        "Cannot decode variable '%s'. Invalid %s: %s"
                        % (ecv.name, ecv.type, repr(v))
                    )
            r[ecv.name] = v
        return r

    @staticmethod
    def decode_str(event, value):
        return value

    @staticmethod
    def decode_int(event, value):
        if value is not None and value.isdigit():
            return int(value)
        return 0

    @staticmethod
    def decode_ipv4_address(event, value):
        return IPv4Parameter().clean(value)

    @staticmethod
    def decode_ipv6_address(event, value):
        return IPv6Parameter().clean(value)

    @staticmethod
    def decode_ip_address(event, value):
        return IPParameter().clean(value)

    @staticmethod
    def decode_ipv4_prefix(event, value):
        return IPv4PrefixParameter().clean(value)

    @staticmethod
    def decode_ipv6_prefix(event, value):
        return IPv6PrefixParameter().clean(value)

    @staticmethod
    def decode_ip_prefix(event, value):
        return PrefixParameter().clean(value)

    @staticmethod
    def decode_mac(event, value):
        return MACAddressParameter().clean(value)

    @staticmethod
    def decode_interface_name(event, value: str):
        return profile_loader.get_profile(event.type.profile)().convert_interface_name(value)

    @staticmethod
    def decode_oid(event, value):
        return value
