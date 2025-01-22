# ----------------------------------------------------------------------
#  RuleSet
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import re
from collections import defaultdict
from typing import Dict, Any, Tuple, Optional

# NOC modules
from .rule import Rule
from .exception import InvalidPatternException, EventProcessingFailed
from .cloningrule import CloningRule
from .rulelookup import RuleLookup
from noc.config import config
from noc.fm.models.cloneclassificationrule import CloneClassificationRule
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.fm.models.enumeration import Enumeration
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
        self.rules: Dict[Tuple[str, str], RuleLookup] = {}  # (profile, chain) -> [rule, ..., rule]
        self.enumerations: Dict[str, Dict[str, str]] = {}  # name -> value -> enumerated
        self.lookup_cls: Optional[RuleLookup] = None
        self.default_rule: Optional[Rule] = None
        #
        is_failed: bool = False
        # metric block
        processed: int = 0

    def load(self):
        """
        Load rules from database
        """
        self.lookup_cls = get_handler(config.classifier.lookup_handler)
        self.rules = {}
        logger.info("Loading rules")
        n = 0
        cn = 0
        profiles = list(profile_loader.iter_profiles())
        rules = defaultdict(list)
        # Load cloning rules
        cloning_rules = []
        for cr in CloneClassificationRule.objects.all():
            try:
                cloning_rules += [CloningRule(cr)]
            except InvalidPatternException as why:
                logger.error("Failed to load cloning rule '%s': Invalid pattern: %s", cr.name, why)
                continue
        logger.info("%d cloning rules found", len(cloning_rules))
        # profiles re cache
        rx_profiles = {}
        # Initialize rules
        for r in EventClassificationRule.objects.order_by("preference"):
            try:
                rule = Rule.from_rule(r, self.enumerations)
            except InvalidPatternException as e:
                logger.error("Failed to load rule '%s': Invalid patterns: %s", r.name, e)
                continue
            # Apply cloning rules
            rs = [rule]
            for cr in cloning_rules:
                if cr.match(rule):
                    try:
                        rs += [Rule.from_rule(r, self.enumerations)]
                        cn += 1
                    except InvalidPatternException as e:
                        logger.error("Failed to clone rule '%s': Invalid patterns: %s", r.name, e)
                        continue
            # Build chain
            for rule in rs:
                # Find profile restrictions
                rule_profiles = rx_profiles.get(rule.profile)
                if not rule_profiles:
                    rx = re.compile(rule.profile)
                    rule_profiles = [p for p in profiles if rx.search(p)]
                    rx_profiles[rule.profile] = rule_profiles
                # Apply rules to appropriative chains
                for p in rule_profiles:
                    rules[p, rule.source.value] += [rule]
                n += 1
        if cn:
            logger.info("%d rules are cloned", cn)
        self.default_rule = Rule.from_rule(
            EventClassificationRule.objects.filter(name=config.classifier.default_rule).first(),
            self.enumerations,
        )
        # Apply lookup solution
        self.rules = {k: self.lookup_cls(rules[k]) for k in rules}
        logger.info("%d rules are loaded in the %d chains", n, len(self.rules))
        #
        self.load_enumerations()

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
        if event.type.source == EventSource.SYSLOG:
            if not event.message:
                return None, None
        # Find rules lookup
        lookup = self.rules.get((event.type.profile, event.type.source.value))
        if lookup:
            for r in lookup.lookup_rules(event, vars):
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
