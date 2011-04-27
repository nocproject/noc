# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activation Engine Daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import os
import time
import datetime
import threading
import logging
import random
import cPickle
import glob
## Django modules
from django.db import reset_queries
## NOC modules
from noc.sa.models import Activator, ManagedObject, MapTask, script_registry,\
                          profile_registry
from noc.fm.models import Event, EventData, EventPriority, EventClass,\
                          EventCategory, IgnoreEventRules
from noc.sa.rpc import RPCSocket, file_hash, get_digest, get_nonce
from noc.pm.models import TimeSeries
from noc.sa.protocols.sae_pb2 import *
from noc.lib.fileutils import read_file
from noc.lib.daemon import Daemon
from noc.lib.debug import error_report, DEBUG_CTX_CRASH_PREFIX
from noc.lib.nbsocket import ListenTCPSocket, AcceptedTCPSocket,\
                             AcceptedTCPSSLSocket, SocketFactory, Protocol,\
                             HAS_SSL

##
## Additions to MANIFEST-ACTIVATfOR file
##
ACTIVATOR_MANIFEST = [
    "sa/profiles/",
    "sa/interfaces/",
]

##
##
##
class Service(SAEService):
    """
    SAE RPC Service handler
    """
    def get_controller_activator(self, controller):
        """
        Get activator for given controller
        
        :param controller: Controller
        :type controller: Controller
        :return: Activator instance
        :rtype: Activator
        """
        return Activator.objects.get(name=controller.stream.pool_name)
    
    def get_activator(self, controller, name, done):
        """
        Get activator and check it is enabled
        """
        # Get activator
        try:
            activator = Activator.objects.get(name=name)
        except Activator.DoesNotExist:
            msg = "Unknown activator '%s'" % name
            logging.error(msg)
            done(controller, error=Error(code=ERR_UNKNOWN_ACTIVATOR,
                                         text=msg))
            return None
        # Check shard is match
        if activator.shard.name not in self.sae.shards:
            msg = "Shard mismatch for '%s'. '%s' is not in %s" % (
                        name, activator.shard.name, self.sae.shards)
            logging.error(msg)
            done(controller, error=Error(code=ERR_INVALID_SHARD,
                                         text=msg))
            return None
        # Check shard is active
        if not activator.shard.is_active:
            msg = "Shard is down: '%s'" % activator.shard.name
            logging.error(msg)
            done(controller, error=Error(code=ERR_SHARD_IS_DOWN,
                                         text=msg))
            return None
        return activator
    
    ##
    ## RPC interfaces
    ##
    def ping(self, controller, request, done):
        """
        Handle RPC ping request.
        """
        done(controller, response=PingResponse())
    
    def register(self, controller, request, done):
        """
        Handle RPC register request
        """
        # Get activator
        activator = self.get_activator(controller, request.name, done)
        if not activator:
            return
        # Requesting digest
        logging.info("Requesting digest for activator '%s'" % request.name)
        r = RegisterResponse()
        r.nonce = get_nonce()
        controller.stream.nonce = r.nonce
        done(controller, response=r)
    
    def auth(self, controller, request, done):
        """
        Handle RPC auth request
        """
        # Get activator
        activator = self.get_activator(controller, request.name, done)
        if not activator:
            return
        # Authenticating
        logging.info("Authenticating activator '%s'" % request.name)
        if (controller.stream.nonce is None or
            get_digest(request.name, activator.auth, controller.stream.nonce) != request.digest):
            done(controller,
                 error=Error(code=ERR_AUTH_FAILED,
                 text="Authencication failed for activator '%s'" % request.name))
            return
        r = AuthResponse()
        controller.stream.is_authenticated = True
        self.sae.join_activator_pool(request.name, controller.stream)
        done(controller, response=r)
    
    def manifest(self, controller, request, done):
        """
        Handle RCP manifest request
        """
        if not controller.stream.is_authenticated:
            done(controller,
                 error=Error(code=ERR_AUTH_REQUIRED,
                             text="Authentication required"))
            return
        done(controller, response=self.sae.activator_manifest)
    
    def software_upgrade(self, controller, request, done):
        """
        Handle RPC software upgrade request
        """
        if not controller.stream.is_authenticated:
            done(controller,
                 error=Error(code=ERR_AUTH_REQUIRED,
                             text="Authentication required"))
            return
        r = SoftwareUpgradeResponse()
        for n in request.names:
            if n not in self.sae.activator_manifest_files:
                done(controller,
                     error=Error(code=ERR_INVALID_UPGRADE,
                                 text="Invalid file requested for upgrade: %s" % n))
                return
            u = r.codes.add()
            u.name = n
            u.code = read_file(n)
        done(controller, response=r)
    
    def set_caps(self, controller, request, done):
        """
        Handle RPC set_caps request
        """
        if not controller.stream.is_authenticated:
            done(controller,
                 error=Error(code=ERR_AUTH_REQUIRED, text="Authentication required"))
            return
        logging.debug("Set capabilities: max_scripts=%d" % request.max_scripts)
        controller.stream.max_scripts = request.max_scripts
        controller.stream.current_scripts = 0
        r = SetCapsResponse()
        done(controller, response=r)
    
    def event_filter(self, controller, request, done):
        """
        Handle RPC event_filter request
        """
        if not controller.stream.is_authenticated:
            done(controller,
                 error=Error(code=ERR_AUTH_REQUIRED,
                             text="Authentication required"))
            return
        activator = self.get_controller_activator(controller)
        r = EventFilterResponse()
        r.expire = self.sae.config.getint("sae", "refresh_event_filter")
        # Build source filter
        for c in ManagedObject.objects.filter(activator=activator, trap_source_ip__isnull=False):
            r.sources.append(c.trap_source_ip)
        # Build event filter
        for ir in IgnoreEventRules.objects.filter(is_active=True):
            i = r.ignore_rules.add()
            i.left_re = ir.left_re
            i.right_re = ir.right_re
        done(controller, response=r)
    
    def event(self, controller, request, done):
        """
        Handle RPC event request
        """
        if not controller.stream.is_authenticated:
            e = Error()
            e.code = ERR_AUTH_REQUIRED
            e.text = "Authentication required"
            done(controller, error=e)
            return
        activator = self.get_controller_activator(controller)
        try:
            if request.ip:
                mo = ManagedObject.objects.get(activator=activator,
                                               trap_source_ip=request.ip)
            else:
                mo = None
        except ManagedObject.DoesNotExist:
            done(controller,
                 error=Error(code=ERR_UNKNOWN_EVENT_SOURCE,
                             text="Unknown event source '%s'" % request.ip))
            return
        self.sae.write_event(
            data=[(b.key, b.value) for b in request.body],
            timestamp=datetime.datetime.fromtimestamp(request.timestamp),
            managed_object=mo
        )
        done(controller, EventResponse())
    
    def pm_data(self, controller, request, done):
        """
        Handle RPC pm_data request
        """
        if not controller.stream.is_authenticated:
            done(controller, error=Error(code=ERR_AUTH_REQUIRED,
                                         text="Authentication required"))
            return
        for d in request.result:
            timestamp = datetime.datetime.fromtimestamp(d.timestamp)
            self.sae.write_event([
                    ("source",      "system"),
                    ("type",        "pm probe"),
                    ("probe_name",  d.probe_name),
                    ("probe_type",  d.probe_type),
                    ("service",     d.service),
                    ("result",      d.result),
                    ("message",     d.message),
                ],
                timestamp=timestamp)
        for d in request.data:
            value = d.value if not d.is_null else None
            TimeSeries.register(d.name, d.timestamp, value)
        done(controller, PMDataResponse())
    

class SAESocket(RPCSocket, AcceptedTCPSocket):
    """
    AcceptedTCPSocket with SAE RPC protocol
    """
    def __init__(self, factory, socket):
        AcceptedTCPSocket.__init__(self, factory, socket)
        RPCSocket.__init__(self, factory.sae.service)
        self.nonce = None
        self.is_authenticated = False
        self.pool_name = None
        
    @classmethod
    def check_access(cls, address):
        return Activator.check_ip_access(address)
    
    def close(self):
        # Rollback all active transactions
        e = Error(code=ERR_ACTIVATOR_LOST,
                  text="Connection with activator lost")
        self.transactions.rollback_all_transactions(e)
        super(AcceptedTCPSocket, self).close()
    
    def set_pool_name(self, name):
        self.pool_name = name
    
    def on_close(self):
        if self.is_authenticated:
            self.factory.sae.leave_activator_pool(self.pool_name, self)
    

##
## SSL version of SAE socket
##
class SAESSLSocket(RPCSocket, AcceptedTCPSSLSocket):
    """
    SSL-aware version of AcceptedTCPSocket with SAE RPC protocol
    """
    def __init__(self, factory, socket, cert):
        AcceptedTCPSSLSocket.__init__(self, factory, socket, cert)
        RPCSocket.__init__(self, factory.sae.service)
        self.nonce = None
        self.is_authenticated = True
    
    @classmethod
    def check_access(cls, address):
        return Activator.check_ip_access(address)
    
    def close(self):
        # Rollback all active transactions
        e = Error(code=ERR_ACTIVATOR_LOST,
                  text="Connection with activator lost")
        self.transactions.rollback_all_transactions(e)
        super(AcceptedTCPSSLSocket, self).close()
    

class SAE(Daemon):
    """
    SAE daemon
    """
    daemon_name = "noc-sae"
    
    def __init__(self):
        self.shards = []
        Daemon.__init__(self)
        logging.info("Running SAE")
        #
        self.service = Service()
        self.service.sae = self
        #
        self.factory = SocketFactory(tick_callback=self.tick)
        self.factory.sae = self
        self.activators = {}  # pool name -> list of activators
        self.object_scripts = {}  # object.id -> # of current scripts
        #
        self.sae_listener = None
        self.sae_ssl_listener = None
        #
        self.activator_manifest = None
        self.activator_manifest_files = None
        #
        t = time.time()
        self.last_crashinfo_check = t
        self.last_mrtask_check = t
        # Activator interface implementation
        self.servers = None
        self.to_save_output = False
        self.use_canned_session = False
        self.log_cli_sessions = False
        self.script_threads = {}
        self.script_lock = threading.Lock()
    
    def load_config(self):
        """
        Reload config and set up shards
        """
        super(SAE, self).load_config()
        self.shards = [s.strip()
                       for s in self.config.get("sae", "shards", "").split(",")]
        logging.info("Serving shards: %s" % ", ".join(self.shards))
    
    def build_manifest(self):
        """
        Build activator manifest
        """
        logging.info("Building manifest")
        manifest = (read_file("MANIFEST-ACTIVATOR").split("\n") +
                    ACTIVATOR_MANIFEST)
        manifest = [x.strip() for x in manifest if x]
        self.activator_manifest = ManifestResponse()
        self.activator_manifest_files = set()
        
        files = set()
        for f in manifest:
            if "*" in f:
                ff = glob.glob(f)
            else:
                ff = [f]
            for g in ff:
                if os.path.isdir(g):
                    for dirpath, dirnames, filenames in os.walk(g):
                        for f in [f for f in filenames if f.endswith(".py")]:
                            files.add(os.path.join(dirpath, f))
                else:
                    files.add(g)
        for f in files:
            self.activator_manifest_files.add(f)
            cs = self.activator_manifest.files.add()
            cs.name = f
            cs.hash = file_hash(f)
    
    def start_listeners(self):
        """
        Start SAE RPC listeners
        """
        # SAE Listener
        sae_listen = self.config.get("sae", "listen")
        sae_port = self.config.getint("sae", "port")
        if (self.sae_listener and
                (self.sae_listener.address != sae_listen or
                 self.sae_listener.port != sae_port)):
            self.sae_listener.close()
            self.sae_listener = None
        if self.sae_listener is None:
            logging.info("Starting SAE listener at %s:%d" % (sae_listen, sae_port))
            self.sae_listener = self.factory.listen_tcp(sae_listen, sae_port, SAESocket)
        # SAE SSL Listener
        if HAS_SSL:
            sae_ssl_listen = self.config.get("sae", "ssl_listen")
            sae_ssl_port = self.config.getint("sae", "ssl_port")
            sae_ssl_cert = self.config.get("sae", "ssl_cert")
            if (self.sae_ssl_listener and
                    (self.sae_ssl_listener.address != sae_ssl_listen or
                     self.sae_ssl_listener.port != sae_ssl_port)):
                self.sae_ssl_listener.close()
                self.sae_ssl_listener = None
            if self.sae_ssl_listener is None:
                logging.info("Starting SAE SSL listener at %s:%d" % (sae_ssl_listen, sae_ssl_port))
                self.sae_ssl_listener = self.factory.listen_tcp(sae_ssl_listen, sae_ssl_port, SAESSLSocket, cert=sae_ssl_cert)
    
    def join_activator_pool(self, name, stream):
        """
        Add registered activator stream to pool
        """
        stream.set_pool_name(name)
        if name not in self.activators:
            self.activators[name] = set()
        logging.info("%s is joining activator pool '%s'" % (repr(stream), name))
        self.activators[name].add(stream)
    
    def leave_activator_pool(self, name, stream):
        """
        Remove activator stream from pool
        """
        if name in self.activators and stream in self.activators[name]:
            logging.info("%s is leaving activator pool '%s'" % (repr(stream), name))
            self.activators[name].remove(stream)
    
    def get_pool_info(self, name):
        """
        Get activator pool information
        """
        if name not in self.activators:
            return {"status": False, "members": 0}
        return {"status": True, "members": len(self.activators[name])}
    
    def run(self):
        """
        Run SAE daemon event loop
        """
        self.build_manifest()
        self.start_listeners()
        self.factory.run(run_forever=True)
    
    def tick(self):
        """
        Called every second. Performs periodic maintainance
        and runs pending Map/Reduce tasks
        """
        t = time.time()
        if t - self.last_crashinfo_check >= 60:
            self.collect_crashinfo()
            self.last_crashinfo_check = time.time()
        reset_queries()  # Clear debug SQL log
        if t - self.last_mrtask_check >= 1:
            # Check Map/Reduce task status
            self.process_mrtasks()
            self.last_mrtask_check = t
    
    def write_event(self, data, timestamp=None, managed_object=None):
        """
        Write FM event to database
        
        :param data: A list of (left, right)
        :param timestamp:
        :param managed_object:
        """
        if managed_object is None:
            managed_object = ManagedObject.objects.get(name="SAE")
        if timestamp is None:
            timestamp = datetime.datetime.now()
        e = Event(
            timestamp=timestamp,
            event_priority=EventPriority.objects.get(name="DEFAULT"),
            event_class=EventClass.objects.get(name="DEFAULT"),
            event_category=EventCategory.objects.get(name="DEFAULT"),
            managed_object=managed_object
            )
        e.save()
        for l, r in data:
            d = EventData(event=e, key=l, value=r)
            d.save()
    
    def collect_crashinfo(self):
        """
        Collect crashinfo and write as FM events
        """
        if not self.config.get("main", "logfile"):
            return
        c_d = os.path.dirname(self.config.get("main", "logfile"))
        if not os.path.isdir(c_d):
            return
        for fn in [fn for fn in os.listdir(c_d) if fn.startswith(DEBUG_CTX_CRASH_PREFIX)]:
            path = os.path.join(c_d, fn)
            if not os.access(path, os.R_OK | os.W_OK):
                # Wait for noc-launcher to fix permissions
                continue
            try:
                with open(path, "r") as f:
                    data = cPickle.loads(f.read())
            except:
                logging.error("Cannot import crashinfo: %s" % path)
                continue
            ts = data["ts"]
            del data["ts"]
            self.write_event(data=data.items(),
                             timestamp=datetime.datetime.fromtimestamp(ts))
            os.unlink(path)
    
    def on_stream_close(self, stream):
        self.streams.unregister(stream)
    
    def get_activator_stream(self, name, for_script=False):
        """
        Select activator for new task. Performs WRR load balancing
        for script tasks and random choice for other ones.
        """
        def weight(a):
            """Load balancing weight"""
            if a.max_scripts == a.current_scripts:
                return 0
            return float(a.max_scripts - a.current_scripts) / a.max_scripts
        
        if name not in self.activators:
            raise Exception("Activator pool '%s' is not available" % name)
        a = self.activators[name]
        if len(a) == 0:
            raise Exception("No activators in pool '%s' available" % name)
        if not for_script:
            return random.choice(list(a))
        # Weighted balancing
        a = sorted(a, lambda x, y: -cmp(weight(x), weight(y)))[0]
        if a.max_scripts == a.current_scripts:
            raise Exception("All activators are busy in pool '%s'" % name)
        return a
    
    def script(self, object, script_name, callback, **kwargs):
        """
        Launch a script
        """
        def script_callback(transaction, response=None, error=None):
            stream.current_scripts -= 1
            if object.profile_name != "NOC.SAE":
                try:
                    self.object_scripts[object.id] -= 1
                except KeyError:
                    pass
            if error:
                logging.error("script(%s,%s,**%s) failed: %s" % (
                                script_name, object, kwargs, error.text))
                callback(error=error)
                return
            result = response.result
            result = cPickle.loads(str(result))  # De-serialize
            callback(result=result)
        
        logging.info("script %s(%s)" % (script_name, object))
        if object.profile_name != "NOC.SAE":
            # Validate activator is present
            try:
                stream = self.get_activator_stream(object.activator.name, True)
            except Exception, why:
                e = Error(code=ERR_ACTIVATOR_NOT_AVAILABLE, text=why)
                logging.error(e.text)
                callback(error=e)
                return
            # Check object's limits
            if object.max_scripts:
                try:
                    o_scripts = self.object_scripts[object.id]
                except KeyError:
                    o_scripts = 0
                if o_scripts >= object.max_scripts:
                    e = Error(code=ERR_OBJ_OVERLOAD,
                              text="Object's script sessions limit exceeded")
                    logging.error(e.text)
                    callback(error=e)
                    return
                self.object_scripts[object.id] = o_scripts + 1
            # Update counters
            stream.current_scripts += 1
        # Build request
        r = ScriptRequest()
        r.script = script_name
        r.access_profile.profile = object.profile_name
        r.access_profile.scheme = object.scheme
        r.access_profile.address = object.address
        if object.port:
            r.access_profile.port = object.port
        if object.user:
            r.access_profile.user = object.user
        if object.password:
            r.access_profile.password = object.password
        if object.super_password:
            r.access_profile.super_password = object.super_password
        if object.remote_path:
            r.access_profile.path = object.remote_path
        if object.snmp_ro:
            r.access_profile.snmp_ro = object.snmp_ro
        if object.snmp_rw:
            r.access_profile.snmp_rw = object.snmp_rw
        attrs = [(a.key, a.value) for a in object.managedobjectattribute_set.all()]
        for k, v in attrs:
            a = r.access_profile.attrs.add()
            a.key = str(k)
            a.value = v
        for k, v in kwargs.items():
            a = r.kwargs.add()
            a.key = str(k)
            a.value = cPickle.dumps(v)
        if object.profile_name == "NOC.SAE":
            self.run_sae_script(r, script_callback)
        else:
            stream.proxy.script(r, script_callback)
    
    def ping_check(self, activator, addresses):
        """
        Send a list of addresses to activator
        and generate fault events for unreachable ones
        """
        def ping_check_callback(transaction, response=None, error=None):
            def save_probe_result(u, result):
                # @todo: Make ManagedObject's method
                mo = ManagedObject.objects.filter(activator=activator, trap_source_ip=u).order_by("id")
                if len(mo) < 1:
                    logging.error("Unknown object in ping_check: %s" % u)
                    return
                # Fetch first-created object in case of multiple objects
                # with same trap_source_ip
                mo = mo[0]
                self.write_event(
                    data=[("source", "system"),
                          ("activator", activator_name),
                          ("probe", "ping"),
                          ("ip", u),
                          ("result", result)],
                    managed_object=mo,
                    timestamp=ts)
            if error:
                logging.error("ping_check failed: %s" % error.text)
                return
            ts = datetime.datetime.now()
            activator_name = activator.name
            for u in response.unreachable:
                save_probe_result(u, "failed")
            for u in response.reachable:
                save_probe_result(u, "success")
        logging.debug("ping_check(%s)" % activator.name)
        try:
            stream = self.get_activator_stream(activator.name, False)
        except:
            e = Error()
            e.code = ERR_ACTIVATOR_NOT_AVAILABLE
            e.text = "Activator '%s' not available" % activator.name
            logging.error(e.text)
            return
        r = PingCheckRequest()
        for a in addresses:
            r.addresses.append(a)
        stream.proxy.ping_check(r, ping_check_callback)
    
    def log_mrt(self, level, task, status, args=None, **kwargs):
        """
        Map/Reduce task logging
        """
        r = [u"MRT task=%d/%d object=%s(%s) script=%s status=%s" % (
                task.task.id, task.id, task.managed_object.name,
                task.managed_object.address, task.map_script, status)]
        if args:
            a = repr(args)
            if level <= logging.INFO and len(a) > 45:
                # Shorten arguments to fit a line
                a = a[:20] + u" ... " + a[-20:]
            r += [u"args=%s" % a]
        if kwargs:
            for k in kwargs:
                r += [u"%s=%s" % (k, kwargs[k])]
        logging.log(level, u" ".join(r))
    
    def process_mrtasks(self):
        """
        Process Map/Reduce tasks
        """
        def map_callback(mt_id, result=None, error=None):
            try:
                mt = MapTask.objects.get(id=mt_id)
            except MapTask.DoesNotExist:
                logging.error("Map task %d suddently disappeared" % mt_id)
                return
            if error:
                # Process non-fatal reasons
                TIMEOUTS = {
                    ERR_ACTIVATOR_NOT_AVAILABLE: 10,
                    ERR_OVERLOAD:                10,
                    ERR_DOWN:                    30,
                }
                if error.code in TIMEOUTS:
                    # Any of non-fatal reasons require retry
                    timeout = TIMEOUTS[error.code]
                    variation = 10
                    timeout = random.randint(-timeout / variation,
                                             timeout / variation)
                    next_try = (datetime.datetime.now() +
                                datetime.timedelta(seconds=timeout))
                    if error.code == ERR_OVERLOAD:
                        next_retries = mt.retries_left
                    else:
                        next_retries = mt.retries_left - 1
                    if mt.retries_left and next_try < mt.task.stop_time:
                        # Check we're still in task time and have retries left
                        self.log_mrt(logging.INFO, task=mt, status="retry")
                        mt.next_try = next_try
                        mt.retries_left = next_retries
                        mt.status = "W"
                        mt.save()
                        return
                mt.status = "F"
                mt.script_result = dict(code=error.code, text=error.text)
                self.log_mrt(logging.INFO, task=mt, status="failed",
                             code=error.code, error=error.text)
            else:
                mt.status = "C"
                mt.script_result = result
                self.log_mrt(logging.INFO, task=mt, status="completed")
            mt.save()
        
        # Additional stack frame to store mt_id in a closure
        def exec_script(mt):
            kwargs = {}
            if mt.script_params:
                kwargs = mt.script_params
            self.log_mrt(logging.INFO, task=mt, status="running", args=kwargs)
            self.script(mt.managed_object, mt.map_script,
                    lambda result=None, error=None: map_callback(mt.id, result, error),
                    **kwargs)
        
        t = datetime.datetime.now()
        for mt in MapTask.objects.filter(status="W", next_try__lte=t,
                    managed_object__activator__shard__is_active=True,
                    managed_object__activator__shard__name__in=self.shards):
            if mt.task.stop_time < t:  # Task timeout
                mt.status = "F"
                mt.script_result = dict(code=ERR_TIMEOUT, text="Timed out")
                mt.save()
                self.log_mrt(logging.INFO, task=mt,
                             status="failed", msg="timed out")
                continue
            mt.status = "R"
            mt.save()
            exec_script(mt)
    
    def run_sae_script(self, request, callback):
        """
        Run internal SAE script
        """
        kwargs = {}
        for a in request.kwargs:
            kwargs[str(a.key)] = cPickle.loads(str(a.value))
        script = script_registry[request.script](profile_registry[request.access_profile.profile],
                                                 self, request.access_profile, **kwargs)
        script.sae = self
        with self.script_lock:
            self.script_threads[script] = callback
            logging.info("%d script threads" % (len(self.script_threads)))
        script.start()
    
    ##
    ##
    ##
    def on_script_exit(self, script):
        logging.info("Script %s(%s) completed" % (script.name,
                                               script.access_profile.address))
        with self.script_lock:
            cb = self.script_threads.pop(script)
            logging.info("%d script threads left" % (len(self.script_threads)))
        if script.result:
            r = ScriptResponse()
            r.result = script.result
            cb(None, response=r)
        else:
            e = Error()
            e.code = ERR_SCRIPT_EXCEPTION
            e.text = script.error_traceback
            cb(None, error=e)
    
    def on_load_config(self):
        """
        Called after config is reloaded by SIGHUP
        """
        self.start_listeners()
    
    ##
    ## Signal handlers
    ##
    def SIGUSR1(self, signo, frame):
        """
        SIGUSR1: Dumps process info
        """
        s = [
            ["factory.sockets", len(self.factory)],
        ]
        logging.info("STATS:")
        for n, v in s:
            logging.info("%s: %s" % (n, v))
        for sock in [s for s in self.factory.sockets.values() if issubclass(s.__class__, RPCSocket)]:
            try:
                logging.info("Activator: %s" % self.factory.get_name_by_socket(sock))
            except KeyError:
                logging.info("Unregistred activator")
            for n, v in sock.stats:
                logging.info("%s: %s" % (n, v))
    
