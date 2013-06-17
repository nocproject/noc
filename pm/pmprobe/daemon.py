## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-pmprobe daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock, Thread
import bisect
import time
import logging
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.stomp.threadclient import ThreadedSTOMPClient
from noc.pm.pmprobe.checks.base import check_registry
from noc.lib.threadpool import Pool
from noc.lib.debug import error_report


class PMProbeDaemon(Daemon):
    daemon_name = "noc-pmprobe"

    def __init__(self, *args, **kwargs):
        self.checks = {}
        self.queue_lock = Lock()
        self.pending_queue = []  # (timestamp, check)
        self.queue_runner_thread = None
        self.thread_pool = None
        self.data_lock = Lock()
        self.data = []
        super(PMProbeDaemon, self).__init__(*args, **kwargs)

    def load_config(self):
        super(PMProbeDaemon, self).load_config()
        self.probe_name = self.config.get("probe", "name")
        self.stomp_host = self.config.get("stomp", "host")
        self.stomp_port = self.config.getint("stomp", "port")
        self.stomp_client_id = "%s_%s" % (
            self.config.get("stomp", "client_id"), self.probe_name)
        self.stomp_login = self.config.get("stomp", "login")
        self.stomp_password = self.config.get("stomp", "password")

    def run(self):
        # Prepare thread pool
        self.thread_pool = Pool()
        # Start queue runner
        self.queue_runner_thread = Thread(target=self.queue_runner)
        self.queue_runner_thread.daemon = True
        self.queue_runner_thread.start()
        # Run STOMP client
        self.stomp_client = ThreadedSTOMPClient(
            host=self.stomp_host,
            port=self.stomp_port,
            login=self.stomp_login,
            passcode=self.stomp_password,
            client_id=self.stomp_client_id
        )
        self.stomp_client.start()
        self.stomp_client.subscribe(
            "/queue/pm/config/%s/" % self.probe_name,
            self.on_config)
        self.stomp_client.send({"probe": self.probe_name},
                               "/queue/pm/config/")
        while self.queue_runner_thread.is_alive():
            self.queue_runner_thread.join(1)

    def on_config(self, destination, body):
        with self.queue_lock:
            for c in body:
                if c["id"] in self.checks:
                    # Change existing check
                    check = self.checks[c["id"]]
                    check.set_config(c["config"])
                    check.set_interval(c["interval"])
                else:
                    # New check
                    logging.debug("Configuring check: "
                                  "%s id=%s config=%s" % (
                        c["check"], c["id"], c["config"]))
                    check = check_registry[c["check"]](
                        self, c["id"], c["config"], c["ts"])
                    check.set_interval(c["interval"])
                    self.checks[c["id"]] = check
                    # Schedule
                    bisect.insort_right(self.pending_queue,
                                        (check.get_next_time(), check))

    def queue_runner(self):
        while True:
            # Run pending tasks
            t = time.time()
            to_sleep = True
            with self.queue_lock:
                while (self.pending_queue and
                       self.pending_queue[0][0] <= t):
                    _, check = self.pending_queue.pop(0)
                    self.thread_pool.run(
                        check.label,
                        self.check_runner, (check,))
                    to_sleep = False
            # Spool pending measurements
            if self.data:
                with self.data_lock:
                    self.stomp_client.send(self.data, "/queue/pm/data/")
                    self.data = []
            elif to_sleep:
                time.sleep(1)  # @todo: Detect time

    def check_runner(self, check):
        """
        Started by thread pool
        :param check:
        :return:
        """
        logging.debug("Running check: %s" % check.label)
        # Apply pending config changes
        check.apply_config()
        # Run check
        timestamp = int(time.time())
        try:
            r = check.handle()
            if r is None:
                # Check failed
                check.error("Failed to collect result")
            else:
                r = check.map_result(r)
                # Spool data
                with self.data_lock:
                    for ts in r:
                        self.data += [(ts, timestamp, r[ts])]
        except:
            error_report()
        logging.debug("Check completed: %s" % check.label)
        # Reschedule check
        with self.queue_lock:
            bisect.insort_right(self.pending_queue,
                                (check.get_next_time(), check))
