## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-collector daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import struct
import logging
import Queue
import itertools
import threading
import datetime
## Third-party modules
from pymongo.mongo_client import MongoClient
from bson import Binary
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.nbsocket.socketfactory import SocketFactory
from noc.lib.debug import error_report


class CollectorDaemon(Daemon):
    daemon_name = "noc-collector"

    def __init__(self, *args, **kwargs):
        self.factory = SocketFactory()
        self.client = None
        self.collection = None
        self.om_collection = None
        self.syslog_collectors = []
        self.trap_collectors = []
        self.queue = Queue.Queue(10000)  # @todo: Configurable
        self.writer_thread = None
        self.om_cache = {}  # ip -> (ttl, object)
        super(CollectorDaemon, self).__init__(*args, **kwargs)

    def load_config(self):
        self.stop_trap_collectors()
        self.stop_syslog_collectors()
        self.stop_db_connection()
        super(CollectorDaemon, self).load_config()
        self.start_db_connection()
        self.start_trap_collectors()
        self.start_syslog_collectors()
        self.activator_name = self.config.get("collector", "name")

    def start_trap_collectors(self):
        """
        Start SNMP Trap Collectors
        """
        if not self.config.getboolean("snmp", "enabled"):
            return
        logging.debug("Starting trap collectors")
        if self.config.getboolean("snmp", "enable_internal_parser"):
            logging.info("Using internal trap parser")
            from noc.sa.activator.trap_collector import TrapCollector
        else:
            logging.info("Using pysnmp trap parser")
            from noc.sa.activator.pysnmp_trap_collector import TrapCollector
        log_traps = False  # self.config.getboolean("main", "log_snmp_traps")
        self.trap_collectors = [
            TrapCollector(self, ip, port, log_traps)
            for ip, port
            in self.resolve_addresses(
                self.config.get("snmp", "listen"), 162)
        ]

    def stop_trap_collectors(self):
        """
        Stop SNMP Trap Collectors
        """
        if self.trap_collectors:
            logging.debug("Stopping trap collectors")
            for tc in self.trap_collectors:
                tc.close()
            self.trap_collectors = []

    def start_syslog_collectors(self):
        """
        Start syslog collectors
        """
        if not self.config.getboolean("syslog", "enabled"):
            return
        logging.debug("Starting syslog collectors")
        from noc.sa.activator.syslog_collector import SyslogCollector
        self.syslog_collectors = [
            SyslogCollector(self, ip, port)
            for ip, port
            in self.resolve_addresses(self.config.get("syslog", "listen"), 514)
        ]

    def stop_syslog_collectors(self):
        """
        Disable syslog collectors
        """
        if self.syslog_collectors:
            logging.debug("Stopping syslog collectors")
            for sc in self.syslog_collectors:
                sc.close()
            self.syslog_collectors = []

    def stop_db_connection(self):
        if self.client:
            logging.debug("Closing database connection")
            self.collection = None
            self.om_collection = None
            self.client.close()
            self.client = None

    def start_db_connection(self):
        logging.debug("Starting MongoClient")
        self.client = MongoClient(
            host=self.config.get("collector_database", "host"),
            port=self.config.getint("collector_database", "port")
        )  # @todo: Setup write concerns
        db_name = self.config.get("collector_database", "name")
        logging.debug("Connection to database %s", db_name)
        db = self.client[db_name]
        self.collection = db[self.config.get("collector_database", "collection")]
        self.om_collection = db[self.config.get("collector_database", "object_map")]
        # @todo: Invalid db and collection

    def run(self):
        logging.info("Running writer thread")
        self.writer_thread = threading.Thread(target=self.writer)
        self.writer_thread._set_daemon()
        self.writer_thread.start()
        logging.info("Running socket factory")
        self.factory.run(run_forever=True)

    def find_object(self, ip):
        """
        Find object in the object_map
        """
        if self.om_collection:
            m = self.om_collection.find_one({"sources": ip}, {"object": 1})
            if m:
                return m["object"]
        return None

    def map_event(self, source):
        """
        Called by collector to resolve managed object by ip
        """
        r = self.om_cache.get(source)
        t = time.time()
        if not r or r[0] < t:
            v = self.find_object(source)
            self.om_cache[source] = (t + 60, v)  # @todo: Configurable
            return v
        else:
            return r[1]

    def on_event(self, timestamp, mo_id, body):
        """
        Called by collector on new event
        """
        ts = datetime.datetime.fromtimestamp(timestamp)
        try:
            self.queue.put((ts, mo_id, body), block=False)
        except Queue.Full:
            pass  # @todo: Log drop

    def writer(self):
        while True:
            try:
                self._writer()
            except:
                error_report()

    def _writer(self):
        def format(ts, mo_id, body):
            s = struct.pack(
                "!II",
                t,
                seq.next() & 0xFFFFFFFFL
            )
            return {
                "timestamp": ts,
                "managed_object": mo_id,
                "raw_vars": body,
                "log": [],
                "seq": Binary(s)
            }

        seq = itertools.count()
        while True:  # @todo: to_shutdown
            # Wait for first item
            t = int(time.time())
            batch = [format(*self.queue.get(block=True))]
            # Collect all pending items
            while True:
                try:
                    batch += [format(*self.queue.get(block=False))]
                except Queue.Empty:
                    break
            # Write
            # @todo: Catch the error
            self.collection.insert(batch, w=1, j=True)
