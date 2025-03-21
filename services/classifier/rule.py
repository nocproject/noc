# ---------------------------------------------------------------------
# Classifier Rule on Partial
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from functools import partial
from dataclasses import dataclass
from typing import List, Optional, Dict, Callable, Any, Tuple, FrozenSet
from types import CodeType

# NOC modules
from noc.core.fm.enum import EventSource
from noc.services.classifier.exception import InvalidPatternException
from noc.fm.models.eventclass import EventClass

rx_escape = re.compile(r"\\(.)")
rx_exact = re.compile(r"^\^?[a-zA-Z0-9%: \-_]+\$?$")
rx_hex = re.compile(r"(?<!\\)\\x([0-9a-f][0-9a-f])", re.IGNORECASE)
rx_named_group = re.compile(r"\(\?P<([^>]+)>")

ANY_VALUE = "*"
safe_builtins = {"str": str, "int": int, "ord": ord, "float": float}


@dataclass(slots=True)
class VarTransformRule:
    name: str
    var: Optional[str] = None
    f_type: Optional[str] = None
    default: Optional[str] = None
    function: Optional[CodeType] = None
    enums: Optional[Dict[str, str]] = None
    args: Optional[List[Any]] = None

    def transform(self, v: Dict[str, Any], var_ctx: Dict[str, Any]):
        if self.f_type == "ifindex":
            # Magic vars name
            v[f"{self.name}__ifindex"] = v[self.var]
        elif self.f_type == "enum":
            v[self.name] = self.enums[self.args[0]][v.pop(self.var).lower()]
        elif self.f_type and self.var in v:
            v[self.name] = getattr(self, self.f_type)(v.pop(self.var))
        if self.function:
            v[self.name] = eval(self.function, {"__builtins__": safe_builtins}, var_ctx)
        elif self.name in var_ctx:
            v[self.name] = var_ctx[self.name]
        elif self.name not in v and self.default:
            v[self.name] = self.default

    @staticmethod
    def int_to_ip(v: str) -> str:
        v = int(v)
        return "%d.%d.%d.%d" % (
            v & 0xFF000000 >> 24,
            v & 0x00FF0000 >> 16,
            v & 0x0000FF00 >> 8,
            v & 0x000000FF,
        )

    @staticmethod
    def bin_to_ip(v: str):
        """
        Fix 4-octet binary ip to dotted representation
        """
        if len(v) != 4:
            return v
        return "%d.%d.%d.%d" % (ord(v[0]), ord(v[1]), ord(v[2]), ord(v[3]))

    @staticmethod
    def bin_to_mac(v):
        """
        Fix 6-octet binary to standard MAC address representation
        """
        if len(v) != 6:
            return v
        return ":".join("%02X" % ord(x) for x in v)

    @staticmethod
    def oid_to_str(v: str):
        """Fix N.c1. .. .cN into "c1..cN" string"""
        x = [int(c) for c in v.split(".")]
        return "".join([chr(c) for c in x[1 : x[0] + 1]])


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    name: str
    event_class: Any
    event_class_name: str
    source: EventSource
    profiles: Optional[FrozenSet[str]] = None
    preference: int = 100
    message_rx: Optional[re.Pattern] = None
    vars: Optional[Dict[str, str]] = None
    vars_transform: Optional[Tuple[VarTransformRule, ...]] = None
    matcher: Optional[Tuple[Callable, ...]] = None
    label_matchers: Optional[Tuple[Callable, ...]] = None
    set_labels: Optional[Tuple[str, ...]] = None
    is_transparent_labels: bool = False
    is_unknown: bool = False
    is_unknown_syslog: bool = False
    to_drop: bool = False

    @classmethod
    def from_config(cls, data: Dict[str, Any], enumerations):
        """Create from EventClassification rule config"""
        matcher, message_rx = [], data["message_rx"] if data["message_rx"] else None
        source = EventSource(data["sources"][0]) if data["sources"] else EventSource.OTHER
        profiles = data.get("profiles") or []
        patterns, transform = [], {}
        for x in data["patterns"]:
            key_s, value_s = x["key_re"].strip("^$"), x["value_re"].strip("^$")
            # Store profile
            if key_s == "profile":
                # profile = value_s.replace("\\", "")
                continue
            elif key_s == "source" and value_s == "SNMP Trap":
                source = EventSource.SNMP_TRAP
            elif key_s == "source" and value_s == "syslog":
                source = EventSource.SYSLOG
            elif key_s == "source":
                continue
            elif key_s == "message":
                message_rx = x["value_re"]
            else:
                # Process key pattern
                m, rxs = cls.get_matcher(x["key_re"], x["value_re"])
                matcher.append(m)
                if rxs:
                    patterns += rxs
        if message_rx:
            patterns += [message_rx]
            message_rx = re.compile(message_rx)
        # Transform
        for pattern in patterns:
            for match in rx_named_group.finditer(pattern):
                name = match.group(1)
                if "__" not in name:
                    continue
                v, fixup, *args = name.split("__")
                if hasattr(VarTransformRule, fixup) or fixup == "enum" or fixup == "ifindex":
                    transform[v] = VarTransformRule(
                        name=v,
                        var=name,
                        f_type=fixup,
                        args=args,
                        enums=enumerations if fixup == "enum" else None,
                    )
                else:
                    print(f"Unknown fixup: {fixup}")
        label_matchers = []
        # Parse Labels
        for x in data["labels"]:
            m = cls.get_label_matcher(
                x["wildcard"], set_var=x.get("set_var"), is_required=x["is_required"]
            )
            if not m:
                continue
            label_matchers.append(m)
        # Parse vars
        for v in data["vars"]:
            value, name = v["value"], v["name"]
            if value.startswith("=") and name not in transform:
                transform[name] = VarTransformRule(
                    name=v["name"], function=compile(value[1:], "<string>", "eval")
                )
            elif value.startswith("=") and name in transform:
                transform[name].function = compile(value[1:], "<string>", "eval")
            elif name in transform:
                transform[name].default = value
            else:
                transform[name] = VarTransformRule(name=name, default=value)
        event_class = EventClass.get_by_name(data["event_class"])
        return Rule(
            id=data["id"],
            name=data["name"],
            event_class=event_class,
            event_class_name=data["event_class"],
            source=source,
            profiles=frozenset(profiles),
            preference=int(data["preference"]),
            message_rx=message_rx,
            matcher=tuple(matcher) if matcher else None,
            vars_transform=tuple(transform.values()),
            label_matchers=tuple(label_matchers) if label_matchers else None,
            # vars=rule_vars,
            to_drop=event_class.action == "D",
        )

    def match(
        self,
        message,
        vars: Dict[str, Any],
        labels: Optional[List[str]] = None,
    ) -> Optional[Dict[str, str]]:
        # if self.source != e.type.source:
        #    return None
        # if self.profile and self.profile != e.type.profile:
        #    return None
        e_vars = {}
        if self.message_rx and message:
            match = self.message_rx.search(message)
            if not match:
                return None
            e_vars.update(match.groupdict())
        for m in self.matcher or []:
            try:
                if not m(vars, e_vars):
                    return None
            except KeyError:
                return None
        if not self.label_matchers:
            return e_vars
        elif not labels:
            return None
        # Labels ctx
        lx = {}
        for ll in labels or []:
            scope, *value = ll.rsplit("::", 1)
            lx[scope] = value[0] if value else None
            lx[ll] = None
        for m in self.label_matchers or []:
            try:
                if not m(lx, e_vars):
                    return None
            except KeyError:
                return None
        return e_vars

    @classmethod
    def get_label_matcher(cls, wildcard, set_var, is_required: bool = True) -> Callable:
        """Create label matcher callable"""
        scope, *value = wildcard.rsplit("::", 1)
        if not value:
            return partial(match_label, set_var=set_var, default_fail=not is_required)
        return partial(
            match_scoped_label, scope, value[0], set_var=set_var, default_fail=not is_required
        )

    @classmethod
    def get_matcher(cls, key_re: str, value_re: str) -> Tuple[Callable, List[str]]:
        """Create variable matcher callable"""
        x_key, rx_key = None, None
        x_value, rx_value = None, None
        rxs = []
        # Process key pattern
        if cls.is_exact(key_re):
            x_key = cls.unescape(key_re.strip("^$"))
        else:
            try:
                rx_key = re.compile(cls.unhex_re(key_re), re.MULTILINE | re.DOTALL)
                rxs.append(key_re)
            except Exception as e:
                raise InvalidPatternException("Error in '%s': %s" % (key_re, e))
        # Process value pattern
        if cls.is_exact(value_re):
            x_value = cls.unescape(value_re.strip("^$"))
        else:
            try:
                rx_value = re.compile(cls.unhex_re(value_re), re.MULTILINE | re.DOTALL)
                rxs.append(value_re)
            except Exception as e:
                raise InvalidPatternException("Error in '%s': %s" % (value_re, e))
        # Save patterns
        if x_key and x_value:
            return partial(match_eq, x_value, x_key), rxs
        elif x_key:
            return partial(match_regex, rx_value, x_key), rxs
        elif x_value:
            return partial(match_k_regex, x_value, rx_key), rxs
        else:
            return partial(match_k_v_regex, rx_value, rx_key), rxs

    @staticmethod
    def unescape(pattern: str) -> str:
        return rx_escape.sub(lambda m: m.group(1), pattern)

    @staticmethod
    def unhex_re(pattern: str) -> str:
        return rx_hex.sub(lambda m: chr(int(m.group(1), 16)), pattern)

    @staticmethod
    def is_exact(pattern: str) -> bool:
        return rx_exact.match(rx_escape.sub("", pattern)) is not None

    @classmethod
    def parse_groups(cls, pattern: str):
        r = {}
        for match in rx_named_group.finditer(pattern):
            name = match.group(1)
            if "__" not in name:
                continue
            v, fixup, *args = name.split("__")
            if hasattr(cls, f"fixup_{fixup}"):
                r[name] = (v, getattr(cls, f"fixup_{fixup}"))
            else:
                print(f"Unknown fixup: {fixup}")
        return r

    def resolve_vars(self, e_vars):
        # Fixup
        # vars transform
        for k in self.vars_transform:
            if k in e_vars:
                e_vars[self.vars_transform[k][0]] = self.vars_transform[k][1](e_vars.pop(k))
        if self.vars:
            e_vars.update(self.vars)


def match_eq(cv: str, field: str, ctx: Dict[str, Any], storage: Dict[str, str]) -> bool:
    return ctx[field] == cv


def match_regex(rx: re.Pattern, field: str, ctx: Dict[str, Any], storage: Dict[str, str]) -> bool:
    match = rx.search(ctx[field])
    if match:
        storage.update(match.groupdict())
        return True
    return False


def match_k_regex(cv: str, field: re.Pattern, ctx: Dict[str, Any], storage: Dict[str, str]) -> bool:
    # To the end match chain, pop ctx
    for k in ctx:
        k_s = field.search(k)
        if k_s and ctx[k] == cv:
            storage.update(k_s.groupdict())
            return True
    return False


def match_k_v_regex(
    rx: re.Pattern, field: re.Pattern, ctx: Dict[str, Any], storage: Dict[str, str]
) -> bool:
    # To the end match chain, pop ctx
    for k in ctx:
        k_s = field.search(k)
        if not k_s:
            continue
        v_s = rx.search(ctx[k])
        if v_s:
            storage.update(k_s.groupdict())
            storage.update(v_s.groupdict())
            return True
    return False


def match_scoped_label(
    scope: str,
    value: str,
    ctx: Dict[str, Optional[str]],
    storage: Dict[str, str],
    set_var: Optional[str] = None,
    default_fail: bool = False,
) -> bool:
    # check scope in labels ctx
    if scope not in ctx:
        return default_fail
    if value != ANY_VALUE and ctx[scope] != value:
        return default_fail
    if set_var and value:
        storage[set_var] = ctx[scope]
    return True


def match_label(
    label: str,
    ctx: Dict[str, str],
    storage: Dict[str, str],
    set_var: Optional[str] = None,
    default_fail: bool = False,
) -> bool:
    # check label value in labels ctx
    if label not in ctx:
        return default_fail
    if set_var and label:
        storage[set_var] = label
    return True


def to_enum(enum: Dict[str, Dict[str, str]], key, value):
    return enum[key][value.lower()]
