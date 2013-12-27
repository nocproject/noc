# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rule
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import logging
import new
## NOC modules
from noc.inv.models import Interface, SubInterface
from noc.lib.datasource import datasource_registry
from exception import InvalidPatternException
from noc.lib.escape import fm_unescape

rx_named_group = re.compile(r"\(\?P<([^>]+)>")


class Rule(object):
    """
    In-memory rule representation
    """

    rx_escape = re.compile(r"\\(.)")
    rx_exact = re.compile(r"^\^[a-zA-Z0-9%: \-_]+\$$")
    rx_hex = re.compile(r"(?<!\\)\\x([0-9a-f][0-9a-f])", re.IGNORECASE)

    def __init__(self, classifier, rule, clone_rule=None):
        self.classifier = classifier
        self.rule = rule
        self.name = rule.name
        if clone_rule:
            self.name += "(Clone %s)" % clone_rule.name
            if classifier.dump_clone:
                # Dump cloned rule
                logging.debug("Rule '%s' cloned by rule '%s'" % (
                    rule.name, clone_rule.name))
                p0 = [(x.key_re, x.value_re) for x in rule.patterns]
                p1 = [(y.key_re, y.value_re) for y in [
                                clone_rule.rewrite(x) for x in rule.patterns]]
                logging.debug("%s -> %s" % (p0, p1))
        self.event_class = rule.event_class
        self.event_class_name = self.event_class.name
        self.is_unknown = self.event_class_name.startswith("Unknown | ")
        self.is_unknown_syslog = self.event_class_name.startswith("Unknown | Syslog")
        self.datasources = {}  # name -> DS
        self.vars = {}  # name -> value
        # Parse datasources
        for ds in rule.datasources:
            self.datasources[ds.name] = eval(
                    "lambda vars: datasource_registry['%s'](%s)" % (
                        ds.datasource,
                        ", ".join(["%s=vars['%s']" % (k, v)
                                   for k, v in ds.search.items()])),
                    {"datasource_registry": datasource_registry}, {})
        # Parse vars
        for v in rule.vars:
            value = v["value"]
            if value.startswith("="):
                value = compile(value[1:], "<string>", "eval")
            self.vars[v["name"]] = value
        # Parse patterns
        c1 = []
        c2 = {}
        c3 = []
        c4 = []
        self.rxp = {}
        self.fixups = set()
        self.profile = None
        for x in rule.patterns:
            if clone_rule:
                # Rewrite, when necessary
                x = clone_rule.rewrite(x)
            x_key = None
            rx_key = None
            x_value = None
            rx_value = None
            # Store profile
            if x.key_re in ("profile", "^profile$"):
                self.profile = x.value_re
                continue
            # Process key pattern
            if self.is_exact(x.key_re):
                x_key = self.unescape(x.key_re[1:-1])
            else:
                try:
                    rx_key = re.compile(self.unhex_re(x.key_re), re.MULTILINE | re.DOTALL)
                except Exception, why:
                    raise InvalidPatternException("Error in '%s': %s" % (x.key_re, why))
            # Process value pattern
            if self.is_exact(x.value_re):
                x_value = self.unescape(x.value_re[1:-1])
            else:
                try:
                    rx_value = re.compile(self.unhex_re(x.value_re), re.MULTILINE | re.DOTALL)
                except Exception, why:
                    raise InvalidPatternException("Error in '%s': %s" % (x.value_re, why))
            # Save patterns
            if x_key:
                c1 += ["'%s' in vars" % x_key]
                if x_value:
                    c1 += ["vars['%s'] == '%s'" % (x_key, x_value)]
                else:
                    c2[x_key] = self.get_rx(rx_value)
            else:
                if x_value:
                    c3 += [(self.get_rx(rx_key), x_value)]
                else:
                    c4 += [(self.get_rx(rx_key), self.get_rx(rx_value))]
        self.to_drop = self.event_class.action == "D"
        self.to_dispose = len(self.event_class.disposition) > 0
        self.compile(c1, c2, c3, c4)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<Rule '%s'>" % self.name

    def get_rx(self, rx):
        n = len(self.rxp)
        self.rxp[n] = rx.pattern
        setattr(self, "rx_%d" % n, rx)
        for match in rx_named_group.finditer(rx.pattern):
            name = match.group(1)
            if "__" in name:
                self.fixups.add(name)
        return n

    def unescape(self, pattern):
        return self.rx_escape.sub(lambda m: m.group(1), pattern)

    def unhex_re(self, pattern):
        return self.rx_hex.sub(lambda m: chr(int(m.group(1), 16)), pattern)

    def is_exact(self, pattern):
        return self.rx_exact.match(self.rx_escape.sub("", pattern)) is not None

    def compile(self, c1, c2, c3, c4):
        """
        Compile native python rule-matching function
        and install it as .match() instance method
        """
        def pyq(s):
            return s.replace("\\", "\\\\").replace("\"", "\\\"")

        e_vars_used = c2 or c3 or c4
        c = []
        if e_vars_used:
            c += ["e_vars = {}"]
        if c1:
            cc = " and ".join(["(%s)" % x for x in c1])
            c += ["if not (%s):" % cc]
            c += ["    return None"]
        if c2:
            cc = ""
            for k in c2:
                c += ["# %s" % self.rxp[c2[k]]]
                c += ["match = self.rx_%s.search(vars['%s'])" % (c2[k], k)]
                c += ["if not match:"]
                c += ["    return None"]
                c += ["e_vars.update(match.groupdict())"]
        if c3:
            for rx, v in c3:
                c += ["found = False"]
                c += ["for k in vars:"]
                c += ["    # %s" % self.rxp[rx]]
                c += ["    match = self.rx_%s.search(k)" % rx]
                c += ["    if match:"]
                c += ["        if vars[k] == '%s':" % v]
                c += ["            e_vars.update(match.groupdict())"]
                c += ["            found = True"]
                c += ["            break"]
                c += ["        else:"]
                c += ["            return None"]
                c += ["if not found:"]
                c += ["    return None"]
        if c4:
            for rxk, rxv in c4:
                c += ["found = False"]
                c += ["for k in vars:"]
                c += ["    # %s" % self.rxp[rxk]]
                c += ["    match_k = self.rx_%s.search(k)" % rxk]
                c += ["    if match_k:"]
                c += ["        # %s" % self.rxp[rxv]]
                c += ["        match_v = self.rx_%s.search(vars[k])" % rxv]
                c += ["        if match_v:"]
                c += ["            e_vars.update(match_k.groupdict())"]
                c += ["            e_vars.update(match_v.groupdict())"]
                c += ["            found = True"]
                c += ["            break"]
                c += ["        else:"]
                c += ["            return None"]
                c += ["if not found:"]
                c += ["    return None"]
        # Vars binding
        if self.vars:
            has_expressions = any(v for v in self.vars.values()
                                  if not isinstance(v, basestring))
            if has_expressions:
                # Callculate vars context
                c += ["var_context = {'event': event}"]
                c += ["var_context.update(e_vars)"]
            for k, v in self.vars.items():
                if isinstance(v, basestring):
                    c += ["e_vars[\"%s\"] = \"%s\"" % (k, pyq(v))]
                else:
                    c += ["e_vars[\"%s\"] = eval(self.vars[\"%s\"], {}, var_context)" % (k, k)]
        if e_vars_used:
            #c += ["return self.fixup(e_vars)"]
            for name in self.fixups:
                r = name.split("__")
                if len(r) == 2:
                    if r[1] in ("ifindex",):
                        # call fixup with managed object
                        c += ["e_vars[\"%s\"] = self.fixup_%s(event.managed_object, fm_unescape(e_vars[\"%s\"]))" % (r[0], r[1], name)]
                    else:
                        c += ["e_vars[\"%s\"] = self.fixup_%s(fm_unescape(e_vars[\"%s\"]))" % (r[0], r[1], name)]
                else:
                    c += ["args = [%s, fm_unescape(e_vars[\"%s\"])]" % (", ".join(["\"%s\"" % x for x in r[2:]]), name)]
                    c += ["e_vars[\"%s\"] = self.fixup_%s(*args)" % (r[0], r[1])]
                c += ["del e_vars[\"%s\"]" % name]
            c += ["return e_vars"]
        else:
            c += ["return {}"]
        c = ["    " + l for l in c]

        cc = ["# %s" % self.name]
        cc += ["def match(self, event, vars):"]
        cc += c
        cc += ["rule.match = new.instancemethod(match, rule, rule.__class__)"]
        c = "\n".join(cc)
        code = compile(c, "<string>", "exec")
        exec code in {"rule": self, "new": new,
                      "logging": logging, "fm_unescape": fm_unescape}

    def clone(self, rules):
        """
        Factory returning clone rules
        """
        pass

    def fixup_int_to_ip(self, v):
        v = long(v)
        return "%d.%d.%d.%d" % (
            v & 0xFF000000 >> 24,
            v & 0x00FF0000 >> 16,
            v & 0x0000FF00 >> 8,
            v & 0x000000FF)

    def fixup_bin_to_ip(self, v):
        """
        Fix 4-octet binary ip to dotted representation
        """
        if len(v) != 4:
            return v
        return "%d.%d.%d.%d" % (ord(v[0]), ord(v[1]), ord(v[2]), ord(v[3]))

    def fixup_bin_to_mac(self, v):
        """
        Fix 6-octet binary to standard MAC address representation
        """
        if len(v) != 6:
            return v
        return ":".join(["%02X" % ord(x) for x in v])

    def fixup_oid_to_str(self, v):
        """
        Fix N.c1. .. .cN into "c1..cN" string
        """
        x = [int(c) for c in v.split(".")]
        return "".join([chr(c) for c in x[1:x[0] + 1]])

    def fixup_enum(self, name, v):
        """
        Resolve v via enumeration name
        @todo: not used?
        """
        return self.classifier.enumerations[name][v.lower()]

    def fixup_ifindex(self, managed_object, v):
        """
        Resolve ifindex to interface name
        """
        ifindex = int(v)
        # Try to resolve interface
        i = Interface.objects.filter(
            managed_object=managed_object.id, ifindex=ifindex).first()
        if i:
            return i.name
        # Try to resolve subinterface
        si = SubInterface.objects.filter(
            managed_object=managed_object.id, ifindex=ifindex).first()
        if si:
            return si.name
        return v