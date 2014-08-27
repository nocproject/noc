## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import inspect
from collections import defaultdict
from collections import namedtuple
import functools
## NOC modules
from noc.lib.solutions import solutions_roots
from match import MatchExpr, MatchTrue


HandlerItem = namedtuple("HandlerItem", ["handler", "match", "req", "opt", "preference"])


class ProbeRegistry(object):
    def __init__(self):
        self.loaded = False
        self.probes = defaultdict(list)  #  metric type -> [probes]

    def load_all(self):
        if self.loaded:
            return
        # Get all probes locations
        dirs = ["pm/probes"]
        for r in solutions_roots():
            d = os.path.join(r, "pm", "probes")
            if os.path.isdir(d):
                dirs += [d]
        # Load all probes
        for root in dirs:
            for path, dirnames, filenames in os.walk(root):
                for f in filenames:
                    if not f.endswith(".py") or f == "__init__.py":
                        continue
                    fp = os.path.join(path, f)
                    mn = "noc.%s" % fp[:-3].replace(os.path.sep, ".")
                    __import__(mn, {}, {}, "*")
        # Order probes by preference
        for mt in self.probes:
            self.probes[mt] = sorted(self.probes[mt],
                                     key=lambda x: x.preference)
        # Prevent further loading
        self.loaded = True

    def register(self, handler, match, req, opt, preference):
        for mt in handler._metrics:
            self.probes[mt] += [
                HandlerItem(handler=handler, match=match,
                            req=req, opt=opt, preference=preference)
            ]

    def iter_handlers(self, metric_type):
        for h in self.probes[metric_type]:
            yield h


probe_registry = ProbeRegistry()


class ProbeBase(type):
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        # Get all decorated members
        for name, value in inspect.getmembers(m):
            # @todo: better checks for unbound methods
            if hasattr(value, "_metrics"):
                mx = value._match_expr
                if not mx:
                    mx = MatchTrue()
                elif len(mx) == 1:
                    mx = mx[0]
                else:
                    mx = reduce(lambda x, y: x | y, mx)
                r, o = mx.get_vars()
                probe_registry.register(value, mx.compile(), r, o,
                                        value._preference)
        return m


class Probe(object):
    __metaclass__ = ProbeBase

    def __init__(self, daemon):
        self.daemon = daemon


class metric(object):
    # Standard preferences
    PREF_VERSION = 100  # Version-depended implementations
    PREF_MODEL = 200  # Model-depended implementations
    PREF_PLATFORM = 300  # Platform-depended implementations
    PREF_VENDOR = 400  # Vendor-depended implementations
    PREF_COMMON = 500  # Common fallback implementations
    # Preferences adjustments
    PREF_BETTER = -10
    PREF_WORSE = 10

    # Conversion methods
    NONE = "none"
    COUNTER = "counter"

    MATCH_OPS = ["eq", "in"]

    def __init__(self, metrics, preference=PREF_COMMON, convert=NONE,
                 **kwargs):
        if isinstance(metrics, basestring):
            metrics = [metrics]
        self.metrics = metrics
        self.preference = preference
        self.convert = convert
        self.selector = kwargs

    def __call__(self, f):
        f._metrics = self.metrics
        f._preference = self.preference
        # Get config options
        spec = inspect.getargspec(f)
        rv, ov = spec.args[1:], []
        if spec.defaults is not None:
            dl = len(spec.defaults)
            ov, rv = rv[-dl:], rv[:-dl]
        # Get match variables
        xrv = getattr(f, "_required_config", [])
        xov = getattr(f, "_opt_config", [])
        mx = getattr(f, "_match_expr", [])
        f._match_expr = mx + self.parse_match(self.selector)
        rv = list(set(xrv + rv))
        ov = list(set(xov + ov) - set(rv))
        #
        f._required_config = rv
        f._opt_config = ov
        f._preference = self.preference
        f._convert = self.convert
        return f

    def parse_match(self, match):
        """
        Returns a tuple of parsed match expressions
        """
        mx = []
        for var in match:
            mv, op = var.rsplit("__", 1)
            if op not in self.MATCH_OPS:
                mv, op = var, "eq"
            mx += [MatchExpr.create(mv, op, match[var])]
        if not len(mx):
            return []
        elif len(mx) == 1:
            return mx
        else:
            return [reduce(lambda x, y: x & y, mx)]


probe_registry.load_all()
