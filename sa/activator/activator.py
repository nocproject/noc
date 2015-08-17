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
        self.to_save_output = False  # Do not save canned result
        self.use_canned_session = False  # Do not use canned session
        logger.info("Loading profile classes")
        profile_registry.register_all()  # Should be performed from ESTABLISHED state
        script_registry.register_all()
        self.nonce = None
        FSM.__init__(self)
        self.script_threads = {}
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
        self.scripts_processed = 0
        self.scripts_failed = 0

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
        with self.script_lock:
            self.script_threads[script] = callback
            logger.info(
                "[%s] Running. Timeout %s [%d/%d threads]",
                script.debug_name,
                timeout,
                len(self.script_threads),
                self.max_script_threads
            )
        script.setDaemon(True)
        script.start()

    def on_script_exit(self, script):
        failed = 1
        if script.e_timeout:
            s = "Timed out"
        elif script.e_cancel:
            s = "Cancelled"
        elif script.e_disconnected:
            s = "CLI lost"
        elif script.login_error:
            s = "Cannot log in"
        else:
            s = "Completed"
            failed = 0
        with self.script_lock:
            cb = self.script_threads.pop(script)
            logger.info(
                "[%s] Stopping. %s [%d/%d threads] (%sms)",
                script.debug_name,
                s,
                len(self.script_threads),
                self.max_script_threads,
                int((time.time() - script.start_time) * 1000)
            )
            self.scripts_processed += 1
            self.scripts_failed += failed
        cb(script)

    def request_call(self, f, *args, **kwargs):
        logger.debug("Requesting call: %s(*%s,**%s)" % (f, args, kwargs))
        self.script_call_queue.put((f, args, kwargs))

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
        # Perform delayed calls
        while not self.script_call_queue.empty():
            try:
                f, args, kwargs = self.script_call_queue.get_nowait()
            except Queue.Empty:
                break
            logger.debug("Calling delayed %s(*%s,**%s)" % (f, args, kwargs))
            apply(f, args, kwargs)
        # Cancel stale scripts
        if self.get_state() == "ESTABLISHED":
            self.cancel_stale_scripts()
        # Run default daemon/fsm machinery
        super(Activator, self).tick()

    @check_state("CONNECTED")
    def protocol(self):
        """ Start protocol negotiation """
        def protocol_callback(transaction, response=None, error=None):
            if self.get_state() != "CONNECTED":
                return
            if error:
                logger.error("Protocol negotiation error: %s", error.text)
                self.event("error")
                return
            if (response.protocol != PROTOCOL_NAME or
                response.version != PROTOCOL_VERSION):
                logger.error("Protocol negotiation failed")
                self.event("error")
                return
            logger.info("Protocol version negotiated")
            self.event("setup")

        logger.info("Negotiation protocol '%s' version '%s'",
                    PROTOCOL_NAME, PROTOCOL_VERSION)
        r = ProtocolRequest(protocol=PROTOCOL_NAME, version=PROTOCOL_VERSION)
        self.sae_stream.proxy.protocol(r, protocol_callback)
    
    @check_state("SETUP")
    def session_setup(self):
        """ Start crypto negotiations"""
        def setup_callback(transaction, response=None, error=None):
            if self.get_state() != "SETUP":
                return
            if error:
                logger.error("Crypto negotiation failed: %s", error.text)
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
                logger.error("Key exchange failed: %s", error.text)
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
                logger.error("Registration error: %s" % error.text)
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
                logger.error("Authentication failed: %s", error.text)
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
            instance=str(self.instance_id)
        )
        self.sae_stream.proxy.auth(r, auth_callback)

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
