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
import time
from collections import defaultdict
from collections import namedtuple
import logging
## Third-party modules
import tornado.gen
## NOC modules
from noc.lib.solutions import solutions_roots
from match import MatchExpr, MatchTrue, MatchCaps
import noc.lib.snmp.consts
from noc.lib.snmp.error import SNMPError, NO_SUCH_NAME
from noc.lib.log import PrefixLoggerAdapter
from noc.core.ioloop.snmp import snmp_get, snmp_count


HandlerItem = namedtuple("HandlerItem", [
    "handler", "handler_name", "match", "req", "opt", "preference",
    "convert", "scale"
])

logger = logging.getLogger(__name__)


class ProbeRegistry(object):
    def __init__(self):
        self.loaded = False
        self.probes = defaultdict(list)  #  metric type -> [HandlerItem]
        self.class_probes = {}  # class name -> metric type -> [HandlerItem]
        self.handlers = {}  # name -> callable
        self.probe_classes = {}  # name -> class
        self.configurable_classes = {}  # name -> class

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

    def register(self, metrics, handler, match, req, opt,
                 preference, convert, scale):
        for mt in metrics:
            hname = self.get_handler_name(handler)
            cn = hname.rsplit(".", 1)[0]
            hi = HandlerItem(
                handler=handler,
                handler_name=hname, match=match,
                req=req, opt=opt, preference=preference,
                convert=convert, scale=scale
            )
            self.probes[mt] += [hi]
            if cn not in self.class_probes:
                self.class_probes[cn] = defaultdict(list)
            self.class_probes[cn][mt] += [hi]
            self.handlers[hname] = handler

    def iter_handlers(self, metric_type):
        for h in self.probes[metric_type]:
            yield h

    def iter_class_handlers(self, cname, metric_type):
        if cname in self.class_probes:
            for h in self.class_probes[cname][metric_type]:
                yield h

    def register_class(self, cls, name):
        if name != "%s.Probe" % cls.__module__:
            self.probe_classes[name] = cls
            if cls.CONFIG_FORM:
                self.configurable_classes[name] = cls

    @classmethod
    def get_handler_name(cls, v):
        return "%s.%s.%s" % (
            v.im_class.__module__,
            v.im_class.__name__,
            v.__name__)

    def get_handler(self, name):
        return self.handlers[name]

    def get_probe_class(self, name):
        return self.probe_classes[name]


probe_registry = ProbeRegistry()


class ProbeBase(type):
    def __new__(mcs, name, bases, attrs):
        m = type.__new__(mcs, name, bases, attrs)
        class_name = "%s.%s" % (m.__module__, m.__name__)
        # Normalize configuration form
        if m.CONFIG_FORM and isinstance(m.CONFIG_FORM, basestring):
            if m.CONFIG_FORM.endswith(".js"):
                m.CONFIG_FORM = m.CONFIG_FORM[:-3]
            if "." not in m.CONFIG_FORM:
                parts = m.__module__.split(".")
                if parts[0] == "noc":
                    parts = parts[1:-1]
                else:
                    parts = parts[:-1]
                m.CONFIG_FORM = "NOC.metricconfig.%s.%s" % (
                    ".".join(parts), m.CONFIG_FORM
                )
            # Check JS path
            parts = m.CONFIG_FORM.split(".")[2:]
            js_parts = parts[:-1] + [parts[-1] + ".js"]
            js_path = os.path.join(*js_parts)
            if not os.path.isfile(js_path):
                logger.error(
                    "Invalid configuration form for probe %s. "
                    "File not found: %s",
                    class_name, js_path
                )
                m._CONFIG_FORM = m.CONFIG_FORM  # Store for update-probe-form
                m.CONFIG_FORM = None
        #
        probe_registry.register_class(
            m, class_name)
        m._METRICS = set()
        # Get all decorated members
        for name, value in inspect.getmembers(m, lambda v: hasattr(v, "_metrics")):
            # Build match expression
            mx = value._match_expr
            if not mx:
                mx = MatchTrue()
            elif len(mx) == 1:
                mx = mx[0]
            else:
                mx = reduce(lambda x, y: x | y, mx)
            mxc = mx.compile()
            mxc._match = mx
            # Build required and optional variables
            r, o = mx.get_vars()
            r |= set(value._required_config)
            o |= set(value._opt_config)
            o -= r
            # Register handler
            for mi in value._metrics:
                m._METRICS.update(mi.metrics)
                probe_registry.register(
                    mi.metrics, value, mxc, r, o,
                    mi.preference, mi.convert, mi.scale
                )
        return m


class Probe(object):
    __metaclass__ = ProbeBase
    # Form class JS file name

    # Human-readable probe title.
    # Means only for human-configurable probes
    TITLE = None
    # Human-readable description
    # Means only for human-configurable probes
    DESCRIPTION = None
    # Human-readable tags for plugin classification.
    # List of strings
    # Means only for human-configurable probes
    TAGS = []
    # Either list of field configuration or
    # string containing full JS class name
    # Means only for human-configurable probes
    CONFIG_FORM = None

    SNMP_v2c = noc.lib.snmp.consts.SNMP_v2c

    INVALID_OID_TTL = 3600

    def __init__(self, daemon, task):
        self.daemon = daemon
        self.task = task
        self.missed_oids = {}  # oid -> expire time
        self.logger = PrefixLoggerAdapter(
            logging.getLogger(self.__module__),
            self.task.uuid
        )

    def disable(self):
        raise NotImplementedError()

    def is_missed_oid(self, oid):
        t = self.missed_oids.get(oid)
        if t:
            if t > time.time():
                return True
            else:
                del self.missed_oids[oid]
        return False

    def set_missed_oid(self, oid):
        self.logger.info("Disabling missed oid %s", oid)
        self.missed_oids[oid] = time.time() + self.INVALID_OID_TTL

    def set_convert(self, metric, convert=None, scale=None):
        """
        Change metric conversions
        """
        self.task.set_metric_convert(metric, convert, scale)

    @classmethod
    def return_result(cls, result):
        """
        Convienent tornado.gen.Return() wrapper
        """
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def snmp_get(self, oids, address, port=161,
                 community="public", version=SNMP_v2c):
        """
        Perform SNMP request to one or more OIDs.
        oids can be string or dict.
        When oid is string returns value
        When oid is dict of <metric type> : oid, returns
        dict of <metric type>: value
        """
        if isinstance(oids, basestring):
            if self.is_missed_oid(oids):
                raise tornado.gen.Return(None)  # Missed oid
        elif isinstance(oids, dict):
            oids = dict(
                (k, v) for k, v in oids.iteritems()
                if not self.is_missed_oid(v)
            )
            if not oids:
                raise tornado.gen.Return(None)  # All oids are missed
        try:
            result = yield snmp_get(
                address, oids, community=str(community),
                port=port, version=version, timeout=3
            )
        except SNMPError, why:
            if why.code == NO_SUCH_NAME:
                # Disable invalid oid
                self.set_missed_oid(why.oid)
            raise tornado.gen.Return(None)
        if isinstance(result, dict):
            for k in result:
                if result[k] is None:
                    self.set_missed_oid(result[k])
        self.return_result(result)

    @tornado.gen.coroutine
    def snmp_getnext(self, oid, address, port=161,
                     community="public", version=SNMP_v2c,
                     bulk=False
                     ):
        """
        Iterator performing SNMP getnext
        requests and yielding oid, value
        """
        for o, v in self.daemon.io.snmp_getnext(
                oid, address, port,
                community=community, version=version, bulk=bulk
        ):
            yield o, v

    def snmp_count(self, oid, address, port=161,
                   community="public", version=SNMP_v2c,
                   filter=None, bulk=False):
        """
        Perform SNMP request to one or more OIDs.
        oids can be string or dict.
        When oid is string returns value
        When oid is dict of <metric type> : oid, returns
        dict of <metric type>: value
        """
        result = yield snmp_count(
            address, oid, community=str(community),
            filter=filter,
            port=port, version=version, timeout=3
        )
        self.return_result(result)


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
    DERIVE = "derive"

    MATCH_OPS = ["eq", "in"]

    def __init__(self, metrics, preference=PREF_COMMON, convert=NONE,
                 scale=1.0, **kwargs):
        if isinstance(metrics, basestring):
            metrics = [metrics]
        self.metrics = metrics
        self.preference = preference
        self.convert = convert
        self.scale = scale
        self.selector = kwargs

    def __call__(self, f):
        if hasattr(f, "_metrics"):
            f._metrics += [self]
        else:
            f._metrics = [self]
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
        if hasattr(f, "_coroutine"):
            return f
        else:
            f._coroutine = True
            return tornado.gen.coroutine(f)

    def parse_match(self, match):
        """
        Returns a tuple of parsed match expressions
        """
        mx = []
        for var in match:
            if var == "caps":
                mx += [MatchCaps(var, match[var])]
                continue
            if "__" in var:
                mv, op = var.rsplit("__", 1)
            else:
                mv, op = var, "eq"
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
