## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BaseCheck
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import inspect
import os
import time
import random
import logging
## NOC modules
from noc.sa.interfaces.base import DictParameter


class BaseCheck(object):
    # Unique handler name
    name = None
    # Handler description
    description = None
    # DictParameter instance to validate output
    parameters = {}
    # List of TS instances
    # For auto-created time series
    time_series = []
    # JS path to form class
    form = None

    def __init__(self, daemon, id, config, ts_map):
        self.daemon = daemon
        self.id = id
        self.config = None
        self.new_config = None
        self.interval = None
        self.t0 = None
        self.label = "%s-%s" % (self.name, id)
        self.ts_map = ts_map
        self.set_config(config)

    def set_config(self, config):
        """
        Replace current config after handle() return
        :param config:
        :return:
        """
        # @todo: Disable check on validation error
        self.new_config = DictParameter(attrs=self.parameters).clean(config)

    def apply_config(self):
        """
        Apply new config.
        Called outside the handle() call
        :return:
        """
        if self.new_config:
            self.config = self.new_config
            self.new_config = None

    def set_interval(self, interval):
        if interval == self.interval:
            return
        self.t0 = time.time() - random.random() * interval
        self.interval = interval

    def get_next_time(self):
        dt = time.time() - self.t0
        n = dt // self.interval
        return self.t0 + (n + 1) * self.interval

    def map_result(self, r):
        o = {}
        for ts in r:
            if ts in self.ts_map:
                o[self.ts_map[ts]] = r[ts]
        return o

    def handle(self):
        """
        Run checks and return dict of time series name -> value
        :return:
        """
        return {}

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.label, msg))

    def info(self, msg):
        logging.info("[%s] %s" % (self.label, msg))

    def error(self, msg):
        logging.error("[%s] %s" % (self.label, msg))

    def get_factory(self):
        return self.daemon.stomp_client.factory


class CheckRegistry(dict):
    def register_all(self):
        prefix = "pm/pmprobe/checks/"
        for f in os.listdir(prefix):
            pp = os.path.join(prefix, f)
            if (not os.path.isdir(pp) or
                    not os.path.isfile(os.path.join(pp, "check.py"))):
                continue
            mn = "noc.pm.pmprobe.checks.%s.check" % f
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and
                        issubclass(o, BaseCheck) and
                        o.__module__.startswith(mn)):
                    assert o.name
                    self[o.name] = o

    @property
    def choices(self):
        return [(x, x) for x in sorted(self)]


class TS(object):
    type = None

    def __init__(self, name):
        self.name = name


class Gauge(TS):
    type = "G"


class Counter(TS):
    type = "C"


class Derive(TS):
    type = "D"

## Load check registry
check_registry = CheckRegistry()
check_registry.register_all()
