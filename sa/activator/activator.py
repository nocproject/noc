# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activator Daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import time
import re
import sys
import random
import bisect
import Queue
import cPickle
from threading import RLock
from collections import defaultdict
## NOC modules
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry
from noc.sa.script.ssh.keys import Key
from noc.sa.rpc import (get_digest,
                        PROTOCOL_NAME, PROTOCOL_VERSION, PUBLIC_KEYS,
                        CIPHERS, MACS, COMPRESSIONS, KEY_EXCHANGES)
from noc.sa.protocols.sae_pb2 import *
from noc.sa.activator.servers import ServersHub
from noc.lib.fileutils import read_file
from noc.lib.daemon import Daemon
from noc.lib.fsm import FSM, check_state
from noc.lib.nbsocket.socketfactory import SocketFactory
from noc.lib.nbsocket.pingsocket import Ping4Socket, Ping6Socket
from noc.sa.activator.service import Service
from noc.sa.activator.activator_socket import ActivatorSocket

logger = logging.getLogger(__name__)


class Activator(Daemon, FSM):
    """
    Activator daemon
    """
    daemon_name = "noc-activator"
    FSM_NAME = "Activator"
    DEFAULT_STATE = "IDLE"
    STATES = {
        ## Starting stage. Activator is idle, all servers are down
        "IDLE": {
            "timeout": "CONNECT",
            "close": "IDLE",
        },
        ## Beginning TCP connection
        "CONNECT": {
            "timeout": "IDLE",
            "refused": "IDLE",
            "close": "IDLE",
            "connect": "CONNECTED",
        },
        ## TCP connection established
        "CONNECTED": {
            "timeout": "IDLE",
            "close": "IDLE",
            "setup": "SETUP",
            "error": "IDLE",
        },
        ## Protocol version negotiated
        ## Crypto algorithms setup
        "SETUP": {
            "timeout": "IDLE",
            "close": "IDLE",
            "error": "IDLE",
            "kex": "KEX",
            "plaintext": "REGISTER"
        },
        ## Key exchange
        "KEX": {
            "timeout": "IDLE",
            "close": "IDLE",
            "error": "IDLE",
            "register": "REGISTER"
        },
        ## Start registration
        "REGISTER": {
            "timeout": "IDLE",
            "close": "IDLE",
            "error": "IDLE",
            "registred": "REGISTRED"
        },
            
        "REGISTRED": {
            "timeout": "IDLE",
            "establish": "ESTABLISHED",
            "close": "IDLE",
            "error": "IDLE",
        },
        "ESTABLISHED": {
            "close": "IDLE",
        }
    }

    def __init__(self):
        Daemon.__init__(self)
        self.activator_name = self.config.get("activator", "name")
        logger.info("Running activator '%s'" % self.activator_name)
        self.service = Service()
        self.service.activator = self
        self.factory = SocketFactory(
            tick_callback=self.tick, controller=self)
        self.children = {}
        self.sae_stream = None
        self.to_listen = self.config.get("activator", "listen_instance") == self.instance_id
        self.ping_count = self.config.getint("activator", "ping_count")
        self.ping_timeout = self.config.getint("activator", "ping_timeout")
        self.to_ping = self.config.get("activator", "ping_instance") == self.instance_id  # To start or not to start ping checks
        if self.to_ping:
            logger.info("Preparing ICMPv4 socket")
            self.ping4_socket = Ping4Socket(self.factory)
            logger.info("Preparing ICMPv6 socket")
            self.ping6_socket = Ping6Socket(self.factory)
        self.object_mappings = {}  # source -> object_id
        self.object_status = {}  # address -> True | False | None
        self.ping_time = []  # (time, address)
        self.ping_offset = {}  # address -> 0..1
        self.ping_interval = {}  # address -> interval
        self.ping_failures = defaultdict(int)  # address -> failure count
        self.ping_failure_threshold = self.config.getint("activator", "ping_failure_threshold")
        self.ping_check_limit = self.config.getint("activator", "ping_check_limit")
        self.running_pings = set()  # address
        self.status_change_queue = []  # [(object_id, new status)]
        self.ignore_event_rules = []  # [(left_re,right_re)]
        self.trap_collectors = []  # List of SNMP Trap collectors
        self.syslog_collectors = []  # List of SYSLOG collectors
        self.to_save_output = False  # Do not save canned result
        self.use_canned_session = False  # Do not use canned session
        logger.info("Loading profile classes")
        profile_registry.register_all()  # Should be performed from ESTABLISHED state
        script_registry.register_all()
        self.nonce = None
        FSM.__init__(self)
        self.next_mappings_update = None
        self.script_threads = {}
        if ((self.to_listen and self.config.getboolean("activator", "dedicated_collector")) or (
            self.to_ping and self.config.getboolean("activator", "dedicated_ping"))):
            self.max_script_threads = 0
        else:
            self.max_script_threads = self.config.getint("activator", "max_scripts")
        self.scripts_processed = 0
        self.scripts_failed = 0
        self.script_lock = RLock()
        self.script_call_queue = Queue.Queue()
        self.servers = ServersHub(self)
        # CLI debug logging
        self.log_cli_sessions = self.config.getboolean("main",
                                                       "log_cli_sessions")
        self.log_cli_sessions_path = self.config.get("main",
                                                     "log_cli_sessions_path")
        self.log_cli_sessions_ip_re = re.compile(self.config.get("main",
                                                "log_cli_sessions_ip_re"))
        self.log_cli_sessions_script_re = re.compile(self.config.get("main",
                                                "log_cli_sessions_script_re"))
        # SSH keys
        self.ssh_public_key = None
        self.ssh_private_key = None
        self.load_ssh_keys()

    def load_ssh_keys(self):
        """
        Initialize ssh keys
        """
        private_path = self.config.get("ssh", "key")
        public_path = private_path + ".pub"
        # Load keys
        self.debug("Loading private ssh key from '%s'" % private_path)
        s_priv = read_file(private_path)
        self.debug("Loading public ssh key from '%s'" % public_path)
        s_pub = read_file(public_path)
        # Check all keys presend
        if s_priv is None or s_pub is None:
            self.error("Cannot find ssh keys. Generate one by './noc generate-ssh-keys' command")
            os._exit(1)
        self.ssh_public_key = Key.from_string(s_pub)
        self.ssh_private_key = Key.from_string_private_noc(s_priv)

    def error(self, msg):
        logger.error(msg)

    def on_IDLE_enter(self):
        """
        Entering IDLE state
        """
        if self.sae_stream:
            self.sae_stream.close()
            self.sae_stream = None
        if self.to_listen:
            if self.trap_collectors:
                self.stop_trap_collectors()
            if self.syslog_collectors:
                self.stop_syslog_collectors()
        self.set_timeout(1)

    def on_CONNECT_enter(self):
        """
        Entering CONNECT state
        """
        self.set_timeout(10)
        self.sae_stream = ActivatorSocket(self.factory,
                                          self.config.get("sae", "host"),
                                          self.config.getint("sae", "port"),
                self.config.get("sae", "local_address"))

    def on_CONNECTED_enter(self):
        """
        Entering CONNECTED state
        """
        self.set_timeout(3)
        self.protocol()

    def on_SETUP_enter(self):
        """
        Entering SETUP state
        """
        self.set_timeout(10)
        self.session_setup()

    def on_KEX_enter(self):
        """
        Entering key exchange state
        """
        self.set_timeout(10)
        self.kex()
    
    def on_REGISTER_enter(self):
        """
        Entering REGISTER state
        """
        self.set_timeout(10)
        self.register()
        
    def on_REGISTRED_enter(self):
        """
        Entering REGISTERED state
        """
        self.set_timeout(10)
        self.auth()

    def on_ESTABLISHED_enter(self):
        """
        Entering ESTABLISHED state
        """
        to_refresh_filters = self.to_ping
        self.next_mappings_update = None
        self.scripts_processed = 0
        self.scripts_failed = 0
        # Check does our instance is designated to listen
        if self.to_listen:
            if self.config.get("activator", "listen_traps"):
                self.start_trap_collectors()
                to_refresh_filters = True
            if self.config.get("activator", "listen_syslog"):
                self.start_syslog_collectors()
                to_refresh_filters = True
        if to_refresh_filters:
            self.get_object_mappings()

    def start_trap_collectors(self):
        """
        Start SNMP Trap Collectors
        """
        logger.debug("Starting trap collectors")
        if self.config.getboolean("activator",
            "enable_internal_trap_parser"):
            logger.info("Using internal trap parser")
            from noc.sa.activator.trap_collector import TrapCollector
        else:
            logger.info("Using pysnmp trap parser")
            from noc.sa.activator.pysnmp_trap_collector import TrapCollector
        log_traps = self.config.getboolean("main", "log_snmp_traps")
        self.trap_collectors = [
            TrapCollector(self, ip, port, log_traps)
            for ip, port
            in self.resolve_addresses(
                self.config.get("activator", "listen_traps"), 162)
        ]

    def stop_trap_collectors(self):
        """
        Stop SNMP Trap Collectors
        """
        if self.trap_collectors:
            logger.debug("Stopping trap collectors")
            for tc in self.trap_collectors:
                tc.close()
            self.trap_collectors = []

    def start_syslog_collectors(self):
        """
        Start syslog collectors
        """
        logger.debug("Starting syslog collectors")
        from noc.sa.activator.syslog_collector import SyslogCollector
        self.syslog_collectors = [
            SyslogCollector(self, ip, port)
            for ip, port
            in self.resolve_addresses(self.config.get("activator", "listen_syslog"), 514)
        ]

    def stop_syslog_collectors(self):
        """
        Disable syslog collectors
        """
        if self.syslog_collectors:
            logger.debug("Stopping syslog collectors")
            for sc in self.syslog_collectors:
                sc.close()
            self.syslog_collectors = []

    def can_run_script(self):
        """
        Check max_scripts limit is not exceeded
        """
        with self.script_lock:
            return len(self.script_threads) < self.max_script_threads

    def run_script(self, object_name, script_name, access_profile, callback,
                   timeout, **kwargs):
        """
        Begin script execution
        """
        pv, pos, sn = script_name.split(".", 2)
        profile = profile_registry["%s.%s" % (pv, pos)]()
        script_class = script_registry[script_name]
        if not timeout:
            timeout = script_class.get_timeout()
        script = script_class(profile, self, object_name, access_profile, timeout, **kwargs)
        logger.info("Script %s(%s). Timeout set to %s" % (script_name,
                                            access_profile.address, timeout))
        with self.script_lock:
            self.script_threads[script] = callback
            logger.info("%d script threads (%d max)" % (
                len(self.script_threads), self.max_script_threads))
        script.start()

    def on_script_exit(self, script):
        failed = 1
        if script.e_timeout:
            s = "is timed out"
        elif script.e_cancel:
            s = "is cancelled"
        elif script.e_disconnected:
            s = "got cli lost"
        elif script.login_error:
            s = "cannot log in"
        else:
            s = "is completed"
            failed = 0
        logger.info("Script %s(%s) %s" % (script.name,
                                           script.debug_name, s))
        with self.script_lock:
            cb = self.script_threads.pop(script)
            logger.info("%d script threads left (%d max)" % (
                len(self.script_threads), self.max_script_threads))
            self.scripts_processed += 1
            self.scripts_failed += failed
        cb(script)

    def request_call(self, f, *args, **kwargs):
        logger.debug("Requesting call: %s(*%s,**%s)" % (f, args, kwargs))
        self.script_call_queue.put((f, args, kwargs))

    def map_event(self, source):
        """
        Map event source to object id
        :param source: Event source
        :type source: str
        :return: object id or None
        :rtype: str or None
        """
        return self.object_mappings.get(source)

    def run(self):
        """
        Main event loop
        """
        self.factory.run(run_forever=True)

    def tick(self):
        """
        Called every second
        """
        t = time.time()
        # Request filter updates
        if (self.get_state() == "ESTABLISHED" and self.next_mappings_update and
            t > self.next_mappings_update):
            self.get_object_mappings()
        # Perform delayed calls
        while not self.script_call_queue.empty():
            try:
                f, args, kwargs = self.script_call_queue.get_nowait()
            except Queue.Empty:
                break
            logger.debug("Calling delayed %s(*%s,**%s)" % (f, args, kwargs))
            apply(f, args, kwargs)
        # Send object status changes
        if self.to_ping and self.get_state() == "ESTABLISHED" and self.status_change_queue:
            self.send_status_change()
        # Cancel stale scripts
        if self.get_state() == "ESTABLISHED":
            self.cancel_stale_scripts()
        # Run pending ping probes
        if self.to_ping and self.get_state() == "ESTABLISHED" and (
                    bool(self.ping4_socket.socket_is_ready()) or
                    bool(self.ping6_socket.socket_is_ready())
        ):
            self.run_ping_checks()
        # Run default daemon/fsm machinery
        super(Activator, self).tick()

    def register_stream(self, stream):
        logger.debug("Registering stream %s" % str(stream))
        self.streams[stream] = None

    def release_stream(self, stream):
        logger.debug("Releasing stream %s" % str(stream))
        del self.streams[stream]

    def reboot(self):
        logger.info("Rebooting")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @check_state("CONNECTED")
    def protocol(self):
        """ Start protocol negotiation """
        def protocol_callback(transaction, response=None, error=None):
            if self.get_state() != "CONNECTED":
                return
            if error:
                logging.error("Protocol negotiation error: %s" % error.text)
                self.event("error")
                return
            if (response.protocol != PROTOCOL_NAME or
                response.version != PROTOCOL_VERSION):
                logging.error("Protocol negotiation failed")
                self.event("error")
                return
            logger.info("Protocol version negotiated")
            self.event("setup")

        logger.info("Negotiation protocol '%s' version '%s'" % (
            PROTOCOL_NAME, PROTOCOL_VERSION))
        r = ProtocolRequest(protocol=PROTOCOL_NAME, version=PROTOCOL_VERSION)
        self.sae_stream.proxy.protocol(r, protocol_callback)
    
    @check_state("SETUP")
    def session_setup(self):
        """ Start crypto negotiations"""
        def setup_callback(transaction, response=None, error=None):
            if self.get_state() != "SETUP":
                return
            if error:
                logging.error("Crypto negotiation failed: %s" % e.text)
                self.event("error")
                return
            if response.key_exchange == "none":
                self.event("plaintext")
            else:
                self.sae_stream.set_next_transform(response.key_exchange,
                                                   response.public_key,
                                                   response.cipher,
                                                   response.mac,
                                                   response.compression)
                self.event("kex")

        r = SetupRequest(
            key_exchanges=KEY_EXCHANGES,
            public_keys=PUBLIC_KEYS,
            ciphers=CIPHERS,
            macs=MACS,
            compressions=COMPRESSIONS
        )
        self.sae_stream.proxy.setup(r, setup_callback)

    @check_state("KEX")
    def kex(self):
        """
        Perform key exchange
        """
        def kex_callback(transaction, response=None, error=None):
            if self.get_state() != "KEX":
                return
            if error:
                logging.error("Key exchange failed: %s" % error.text)
                self.event("error")
                return
            self.sae_stream.complete_kex(response)
            self.sae_stream.activate_next_transform()
            self.event("register")

        self.sae_stream.start_kex(kex_callback)

    @check_state("REGISTER")
    def register(self):
        def register_callback(transaction, response=None, error=None):
            if self.get_state() != "REGISTER":
                return
            if error:
                logging.error("Registration error: %s" % error.text)
                self.event("error")
                return
            logger.info("Registration accepted")
            self.nonce = response.nonce
            self.event("registred")
        logger.info("Registering as '%s'" % self.config.get("activator", "name"))
        r = RegisterRequest()
        r.name = self.activator_name
        self.sae_stream.proxy.register(r, register_callback)

    @check_state("REGISTRED")
    def auth(self):
        def auth_callback(transaction, response=None, error=None):
            if self.get_state() != "REGISTRED":
                return
            if error:
                logging.error("Authentication failed: %s" % error.text)
                self.event("error")
                return
            logger.info("Authenticated")
            self.event("establish")
        name = self.config.get("activator", "name")
        logger.info("Authenticating as %s" % name)
        r = AuthRequest(
            name=name,
            digest=get_digest(name,
                              self.config.get("activator", "secret"),
                              self.nonce),
            max_scripts=self.max_script_threads,
            instance=str(self.instance_id),
            can_ping=bool(self.to_ping)
        )
        self.sae_stream.proxy.auth(r, auth_callback)

    @check_state("ESTABLISHED")
    def refresh_object_mappings(self):
        self.get_object_mappings()

    @check_state("ESTABLISHED")
    def get_object_mappings(self):
        def object_mappings_callback(transaction, response=None, error=None):
            if error:
                logging.error("get_object_mappings error: %s" % error.text)
                return
            self.object_mappings = dict((x.source, x.object)
                                        for x in response.mappings)
            self.compile_ignore_event_rules(response.ignore_rules)
            self.debug("Setting object mappings to: %s" % self.object_mappings)
            self.next_mappings_update = time.time() + response.expire
            #
            if not self.object_status:
                self.object_status = dict(
                    (x.address, x.current_status)
                    for x in response.ping
                    if x.current_status is not None
                )
            # Schedule ping checks
            self.ping_interval = dict((x.address, x.interval)
                for x in response.ping)
            self.ping_time = [(t, a) for t, a in self.ping_time
                              if a in self.ping_interval]
            self.running_pings = set(
                a for a in self.running_pings if a in self.ping_interval)
            n = set(self.ping_interval) - (set(a for f, a in self.ping_time) | set(self.running_pings))
            if n:
                # New mappings
                for a in n:
                    self.ping_offset[a] = random.random()
                self.ping_time += [(self.get_next_ping_time(a), a) for a in n]
                self.ping_time = sorted(self.ping_time)
            self.debug("Scheduling ping probes to: %s" % self.ping_time)

        logger.info("Requesting object mappings")
        # Delay next request to at least 1 minute
        self.next_mappings_update = time.time() + 60
        # Request object mappings
        r = ObjectMappingsRequest()
        self.sae_stream.proxy.object_mappings(r, object_mappings_callback)

    def on_event(self, timestamp, object, body):
        """
        Send FM event to SAE
        :param timestamp: Event timestamp
        :param object: Object id
        :param body: Event content
        """
        def on_event_callback(transaction, response=None, error=None):
            if error:
                logging.error("event_proxy failed: %s" % error)
        r = EventRequest()
        r.timestamp = timestamp
        r.object = object
        for k, v in body.items():
            # Check ignore rules
            for lr, rr in self.ignore_event_rules:
                if lr.search(k) and rr.search(v):
                    return  # Ignore event
            # Populate event request
            i = r.body.add()
            i.key = str(k)
            i.value = str(v)
        self.sae_stream.proxy.event(r, on_event_callback)

    def queue_status_change(self, address, status):
        i = self.object_mappings.get(address)
        if i:
            self.status_change_queue += [(i, status)]

    def send_status_change(self):
        def status_change_callback(transaction, response=None, error=None):
            if error:
                logging.error("object_status failed: %s" % error)

        r = ObjectStatusRequest()
        for object, status in self.status_change_queue:
            s = r.status.add()
            s.object = object
            s.status = status
        self.status_change_queue = []
        self.sae_stream.proxy.object_status(r, status_change_callback)

    def compile_ignore_event_rules(self, rules):
        ir = []
        for r in rules:
            try:
                logger.debug("Adding ignore rule: %s | %s" % (r.left_re,
                                                               r.right_re))
                ir += [(re.compile(r.left_re, re.IGNORECASE),
                        re.compile(r.right_re, re.IGNORECASE))]
            except re.error, why:
                logging.error("Failed to compile ignore event rule: %s,%s. skipping" % (l, r))
        self.ignore_event_rules = ir

    @check_state("ESTABLISHED")
    def cancel_stale_scripts(self):
        """
        Cancel stale scripts
        """
        with self.script_lock:
            to_cancel = [st for st in self.script_threads
                         if st.is_stale() and not st.e_cancel]
            for script in to_cancel:
                logger.info("Cancelling stale script %s(%s)" % (
                    script.name, script.access_profile.address))
                script.cancel_script()

    def run_ping_checks(self):
        if not self.ping_time:
            return
        i = bisect.bisect_right(self.ping_time, (time.time(), None))
        while i > 0:
            t, a = self.ping_time.pop(0)
            self.debug("PING %s" % a)
            self.running_pings.add(a)
            sock = self.ping6_socket if ":" in a else self.ping4_socket
            if sock.socket_is_ready():
                sock.ping(
                    a, count=self.ping_count, timeout=self.ping_timeout,
                    callback=self.ping_callback, stop_on_success=True)
            else:
                logger.debug("Ignoring ping %s: Socket is not ready", a)
            i -= 1

    def ping_callback(self, address, result):
        # Pessimistic: Fail if any ping failed
        # status = bool(len(result) == len([r for r in result if r is not None]))
        # Optimistic: Fail if all pings failed
        status = len([r for r in result if r is not None]) > 0
        if address in self.running_pings:
            # Return to schedule
            self.running_pings.remove(address)
            bisect.insort_right(
                self.ping_time,
                (self.get_next_ping_time(address), address))
        old_status = self.object_status.get(address)
        if old_status is False and status is True:
            # Reset failures count
            self.ping_failures[address] = 0
        elif old_status is True and status is False:
            # Check failure threshold
            self.ping_failures[address] += 1
            if self.ping_failures[address] < self.ping_failure_threshold:
                status = True  # Failure confirmation needed
        self.debug("PING %s: Result %s [%s -> %s]" % (
            address, result, old_status, status))
        if status != old_status:
            # Status changed
            self.object_status[address] = status
            self.queue_status_change(address, status)

    def get_next_ping_time(self, address):
        i = self.ping_interval.get(address, 60)
        t = time.time()
        istart = (int(t) // i) * i
        delta = i * self.ping_offset[address]
        n = istart + delta
        if n > t:
            return n
        else:
            return n + i

    def ping_check(self, addresses, callback):
        """
        Ping addresses
        """
        def spool():
            while left and len(running) < self.ping_check_limit:
                a = left.pop(0)
                running.add(a)
                self.ping4_socket.ping(
                    a, count=self.ping_count, timeout=self.ping_timeout,
                    callback=cb, stop_on_success=True)

        def cb(address, result):
            r = bool([x for x in result if x is not None])
            status.append((address, r))
            if len(status) == la:
                callback(status)
            else:
                running.remove(address)
                spool()  # Run next batch

        status = []
        la = len(addresses)
        left = [a for a in addresses]
        running = set()
        spool()  # Run first batch

    def get_status(self):
        s = {
            "timestamp": int(time.time()),
            "pool": self.activator_name,
            "instance": self.instance_id,
            "state": self._current_state,
            "last_state_change": int(self._state_enter_time),
            "max_scripts": self.max_script_threads,
            "scripts_processed": self.scripts_processed,
            "scripts_failed": self.scripts_failed
        }
        with self.script_lock:
            s["current_scripts"] = len(self.script_threads)
            ss = []
            for script in self.script_threads:
                ss += [{
                    "script": script.name,
                    "object_name": script.object_name,
                    "address": script.access_profile.address,
                    "start_time": int(script.start_time),
                    "timeout": script._timeout
                }]
            s["scripts"] = ss
        return s

    def SIGUSR1(self, signo, frame):
        """
        SIGUSR1 returns process info
        """
        s = [
            ["factory.sockets", len(self.factory)],
        ]
        if self.sae_stream:
            s += self.sae_stream.stats
        logger.info("STATS:")
        for n, v in s:
            logger.info("%s: %s" % (n, v))

    # SIGCHLD: Zombie hunting
    def SIGCHLD(self, signo, frame):
        """
        SIGCHLD begins zombie hunting
        """
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
            except OSError:
                break
            if pid:
                logger.debug("Zombie pid=%d is hunted down and mercilessly killed" % pid)
            else:
                break
