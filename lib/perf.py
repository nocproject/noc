## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performance measurements
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import os

ENABLE_STATS = False
BASE_DIR = None

metrics = {}


class Metric(object):
    """
    Performance metric
    """
    def __init__(self, name):
        self.name = name
        metrics[name] = self
        self.value = 0
        self.calls = []

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def __add__(self, other):
        self.value += other
        return self

    def __iadd__(self, other):
        self.value += other
        return self

    def __sub__(self, other):
        self.value -= other
        return self

    def __isub__(self, other):
        self.value -= other
        return self

    def timer(self, stream=None, *args):
        return Timer(self, stream, stream, *args)


class Timer(object):
    """
    Timer context managed. Called by Metric.timer()
    """
    OK = "OK"
    FAIL = "FAIL"
    EXCEPTION = "EXCEPTION"

    def __init__(self, metric, stream=None, *args):
        self.metric = metric
        self.stream = stream
        self.args = args
        self.result = self.OK

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        dt = time.time() - self.t0
        self.metric += dt
        if exc_type:
            self.result = self.EXCEPTION
        if ENABLE_STATS and BASE_DIR and self.stream:
            T = time.localtime(self.t0)
            msg = ",".join(
                [
                    time.strftime("%Y-%m-%d %H:%M:%S%Z"),
                    self.result, "%.2f" % (dt * 1000)
                ] + list(self.args[1:])
            )
            bd = os.path.join(
                BASE_DIR, "%4d/%02d/%02d" % (T[0], T[1], T[2]))
            fn = "%s.log" % self.stream
            if not os.path.isdir(bd):
                try:
                    os.makedirs(bd)
                except OSError:
                    pass
            with open(os.path.join(bd, fn), "a") as f:
                f.write(msg + "\n")

    def fail(self):
        self.result = self.FAIL


def enable_stats(enabled=True, base_dir=None):
    global ENABLE_STATS, BASE_DIR
    ENABLE_STATS = enabled
    if base_dir:
        BASE_DIR = base_dir
