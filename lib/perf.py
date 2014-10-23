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
import logging
import socket

logger = logging.getLogger(__name__)

ENABLE_STATS = False
BASE_DIR = None
REPORT_COLLECTOR = None
REPORT_INTERVAL = None
METRICS_PER_PACKET = 15

metrics = {}


class Metric(object):
    """
    Performance metric
    """
    def __init__(self, name):
        logger.debug("Creating metric %s", name)
        self.name = name
        metrics[name] = self
        self.value = 0
        self.calls = []

    def set(self, value):
        if isinstance(value, Metric):
            self.value = value.value
        else:
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

    RMAP = {
        "S": OK,
        "F": FAIL,
        "X": EXCEPTION
    }

    def __init__(self, metric, stream=None, *args):
        self.metric = metric
        self.stream = stream
        self.args = args
        self.result = self.OK

    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        t1 = time.time()
        dt = t1 - self.t0
        self.metric += dt
        if exc_type:
            self.result = self.EXCEPTION
        self.log(self.t0, t1, self.result)

    def fail(self):
        self.result = self.FAIL

    def log(self, t0, t1, result):
        if ENABLE_STATS and BASE_DIR and self.stream:
            result = self.RMAP.get(result, result)
            dt = t1 - t0
            T = time.localtime(t0)
            msg = ",".join(
                [
                    time.strftime("%Y-%m-%d %H:%M:%S%Z"),
                    result, "%.2f" % (dt * 1000)
                ] + list(str(x) for x in self.args[1:])
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


class MetricsHub(object):
    def __init__(self, prefix, *args):
        self._prefix = prefix
        if not self._prefix.endswith("."):
            self._prefix += "."
        for a in args:
            self._add_metric(a)

    def _add_metric(self, name):
        m = Metric(self._prefix + name)
        setattr(self, name.replace(".", "_").replace("-", "_"), m)
        return m

    def __setattr__(self, key, value):
        if key.startswith("_") or key not in self.__dict__:
            self.__dict__[key] = value
        else:
            self.__dict__[key].set(value)


def enable_stats(enabled=True, base_dir=None,
                 report_collector=None, report_interval=60):
    global ENABLE_STATS, BASE_DIR, REPORT_COLLECTOR, REPORT_INTERVAL
    ENABLE_STATS = enabled
    logger.info("Stats are %s", "enabled" if enabled else "disabled")
    if base_dir:
        logger.info("Timing base directory is %s", base_dir)
        BASE_DIR = base_dir
    if report_collector:
        logger.info(
            "Reporting performance metrics to udp://%s every %s secords",
            report_collector, report_interval
        )
        addr, port = report_collector.split(":")
        REPORT_COLLECTOR = (addr, int(port))
        REPORT_INTERVAL = report_interval
        # Run reporter thread
        import threading
        logger.info("Running reporter thread")
        t = threading.Thread(name="perf", target=reporter)
        t.daemon = True
        t.start()


def dump():
    """Dump all metrics"""
    for m in sorted(metrics):
        print "%s: %s" % (m, metrics[m].get())


def reporter():
    """Report thread handler"""
    global REPORT_COLLECTOR, REPORT_INTERVAL
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while REPORT_COLLECTOR:
        time.sleep(REPORT_INTERVAL)
        ts = int(time.time())
        data = [
            "%s %s %s\n" % (m, metrics[m].get(), ts)
            for m in metrics
        ]
        while data:
            msg = "".join(data[:METRICS_PER_PACKET])
            data = data[METRICS_PER_PACKET:]
            logger.debug("Sending to udp://%s:\n%s",
                         REPORT_COLLECTOR, msg)
            try:
                sock.sendto(msg, REPORT_COLLECTOR)
            except socket.error, why:
                logger.info("Socket error: %s", why)
