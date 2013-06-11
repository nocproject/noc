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


class BaseCheck(object):
    # Unique handler name
    name = None
    # Handler description
    description = None
    # DictParameter instance to validate output
    parameters = {}
    # Name of derived time series
    time_series = []
    # JS path to form class
    form = None

    def __init__(self, daemon, id, config, ts_map):
        self.daemon = daemon
        self.id = id
        self.config = config
        self.new_config = None
        self.interval = None
        self.t0 = None
        self.label = "%s-%s" % (self.name, id)
        self.ts_map = ts_map

    def set_config(self, config):
        """
        Replace current config after handle() return
        :param config:
        :return:
        """
        self.new_config = config

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

check_registry = CheckRegistry()
check_registry.register_all()
