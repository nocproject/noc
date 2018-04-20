# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activation Engine Daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import time
import datetime
import threading
import logging
import random
import cPickle
import sys
import csv
import itertools
import struct
from collections import defaultdict
## Django modules
from django.db import reset_queries
# Third-party modules
from bson import Binary
## NOC modules
from noc.sa.sae.service import Service
from noc.sa.sae.sae_socket import SAESocket
from noc.main.models import Shard
from noc.sa.models import (Activator, ManagedObject, MapTask, ReduceTask,
                           script_registry, profile_registry,
                           ActivatorCapabilitiesCache, FailedScriptLog)
from noc.fm.models import NewEvent
from noc.sa.rpc import RPCSocket
from noc.sa.protocols.sae_pb2 import *
from noc.lib.daemon import Daemon
from noc.lib.nbsocket import SocketFactory
from noc.lib.ip import IP
from noc.lib.dateutils import total_seconds


class SAE(Daemon):
    """
    SAE daemon
    """
    daemon_name = "noc-sae"

    def __init__(self):
        self.shards = []
        self.single_shard = False
        self.force_plaintext = []
        #
        self.strip_syslog_facility = False
        self.strip_syslog_severity = False
        #
        self.has_getsizeof = hasattr(sys, "getsizeof")
        # Connection rate throttling
        self.max_mrt_rate_per_sae = None
        self.max_mrt_rate_per_shard = None
        #
        self.mrt_log = False
        self.mrt_log_dir = None
        #
        self.event_seq = itertools.count()
        # Initialize daemon
        Daemon.__init__(self)
        self.logger.info("Running SAE")
        #
        self.service = Service()
        self.service.sae = self
        #
        self.factory = SocketFactory(tick_callback=self.tick)
        self.factory.sae = self
        self.activators = defaultdict(set)  # pool name -> set of activators
        self.object_scripts = {}  # object.id -> # of current scripts
        self.object_status = {}  # object.id -> last ping check status
        #
        self.sae_listener = None
        self.sae_ssl_listener = None
        #
        self.mo_cache = {}  # object_id -> Managed Object
        #
        t = time.time()
        self.last_mrtask_check = t
        self.last_status_refresh = t
        # Activator interface implementation
        self.servers = None
        self.to_save_output = False
        self.use_canned_session = False
        self.log_cli_sessions = False
        self.script_threads = {}
        self.script_lock = threading.Lock()
        #
        self.blocked_pools = set()  # Blocked activator names
        #
        self.default_managed_object = None
        #
        self.event_batch = None
        self.batched_events = 0
        self.prepare_event_bulk()

    def load_config(self):
        """
        Reload config and set up shards
        """
        super(SAE, self).load_config()
        self.shards = [s.strip()
                       for s in self.config.get("sae", "shards", "").split(",")]
        self.single_shard = Shard.objects.filter(is_active=True).count() == 1 and len(self.shards) == 1
        self.logger.info(
            "Serving shards: %s%s",
            ", ".join(self.shards),
            " (single shard)" if self.single_shard else "(multi shard)"
        )
        self.force_plaintext = [IP.prefix(p) for p
                in self.config.get("sae", "force_plaintext").strip().split(",")
                if p]
        self.strip_syslog_facility = self.config.getboolean("event",
                                                    "strip_syslog_facility")
        self.strip_syslog_severity = self.config.getboolean("event",
                                                    "strip_syslog_severity")
        self.max_mrt_rate_per_sae = self.config.getint("sae",
                                                    "max_mrt_rate_per_sae")
        self.max_mrt_rate_per_shard = self.config.getint("sae",
                                                    "max_mrt_rate_per_shard")
        self.mrt_log = (self.options.daemonize and
                        self.config.getboolean("main", "mrt_log"))
        if self.mrt_log:
            ld = os.path.dirname(self.config.get("main", "logfile"))
            self.mrt_log_dir = os.path.join(ld, "mrt")
            if not os.path.isdir(self.mrt_log_dir):
                os.mkdir(self.mrt_log_dir)
        # Settings
        self.mrt_schedule_interval = 1
        self.activator_status_interval = 60
        #

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
            self.logger.info("Starting SAE listener at %s:%d" % (sae_listen, sae_port))
            self.sae_listener = self.factory.listen_tcp(sae_listen, sae_port, SAESocket)

    def update_activator_capabilities(self, pool):
        """
        Update activator cabapilities cache
        :param pool: Pool name
        """
        members = len(self.activators[pool])
        max_scripts = 0
        for s in self.activators[pool]:
            if hasattr(s, "max_scripts"):
                max_scripts += s.max_scripts
        a = Activator.objects.get(name=pool)
        c = a.update_capabilities(members=members, max_scripts=max_scripts)
        self.logger.info("Activator pool '%s' capability: members=%d, sessions=%d" % (
            pool, c.members, c.max_scripts))
        return c

    def join_activator_pool(self, name, stream):
        """
        Add registered activator stream to pool
        """
        stream.set_pool_name(name)
        self.logger.info("%s is joining activator pool '%s'" % (repr(stream), name))
        self.activators[name].add(stream)
        c = self.update_activator_capabilities(name)
        self.write_event({
            "source": "system",
            "event": "activator_join",
            "name": name,
            "instance": stream.instance,
            "sessions": stream.max_scripts,
            "pool_members": c.members,
            "pool_sessions": c.max_scripts,
            "min_members": c.activator.min_members,
            "min_sessions": c.activator.min_sessions
        })

    def leave_activator_pool(self, name, stream):
        """
        Remove activator stream from pool
        """
        if stream not in self.activators[name]:
            return
        self.logger.info("%s is leaving activator pool '%s'" % (
            repr(stream), name))
        self.activators[name].remove(stream)
        c = self.update_activator_capabilities(name)
        self.write_event({
            "source": "system",
            "event": "activator_leave",
            "name": name,
            "instance": stream.instance,
            "sessions": stream.max_scripts,
            "pool_members": c.members,
            "pool_sessions": c.max_scripts,
            "min_members": c.activator.min_members,
            "min_sessions": c.activator.min_sessions
        })

    def get_pool_info(self, name):
        """
        Get activator pool information
        """
        members = len(self.activators["name"])
        return {
            "status": members > 0,
            "members": members
        }

    def run(self):
        """
        Run SAE daemon event loop
        """
        self.logger.info("Cleaning activator capabilities cache")
        ActivatorCapabilitiesCache.reset_cache(self.shards)
        self.check_activator_thresholds()
        self.start_listeners()
        self.factory.run(run_forever=True)

    def check_activator_thresholds(self):
        """
        Check activator sessions thresholds
        """
        self.logger.info("Checking activator thresholds")
        for a in Activator.objects.filter(is_active=True, shard__name__in=self.shards):
            if a.min_sessions or a.min_members:
                self.logger.info("   activator pool '%s' has lower thresholds" % a.name)
                self.write_event({
                    "source": "system",
                    "event": "activator_join",
                    "name": a.name,
                    "instance": "0",
                    "sessions": 0,
                    "pool_members": 0,
                    "pool_sessions": 0,
                    "min_members": a.min_members,
                    "min_sessions": a.min_sessions
                })

    def tick(self):
        """
        Called every second. Performs periodic maintainance
        and runs pending Map/Reduce tasks
        """
        t = time.time()
        reset_queries()  # Clear debug SQL log
        if self.batched_events:
            self.logger.info("Writing %d batched events", self.batched_events)
            self.event_batch.execute({"w": 0})
            self.prepare_event_bulk()
        if t - self.last_mrtask_check >= self.mrt_schedule_interval:
            # Check Map/Reduce task status
            self.process_mrtasks()
            self.last_mrtask_check = t
        if t - self.last_status_refresh >= self.activator_status_interval:
            self.refresh_activator_status()

    def write_event(self, data, timestamp=None, managed_object=None):
        """
        Write FM event to database

        :param data: A list of (key, value) or dict
        :param timestamp:
        :param managed_object: Managed object
        """
        if managed_object is None:
            # Set object to SAE, if not set
            if not self.default_managed_object:
                self.default_managed_object = ManagedObject.objects.get(name="SAE")
            managed_object = self.default_managed_object
        if timestamp is None:
            timestamp = datetime.datetime.now()
        if type(data) == list:
            data = dict(data)
        elif type(data) != dict:
            raise ValueError("List or dict type required")
        # Strip syslog facility if required
        if (self.strip_syslog_facility and "source" in data
            and data["source"] == "syslog" and "facility" in data):
            del data["facility"]
        # Strip syslog severity if required
        if (self.strip_syslog_severity and "source" in data
            and data["source"] == "syslog" and "severity" in data):
            del data["severity"]
        # Normalize data
        data = dict(
            (str(k).replace(".", "__").replace("$", "^^"), str(data[k]))
            for k in data
        )
        # Generate sequental number
        seq = Binary(struct.pack(
            "!II",
            int(time.time()),
            self.event_seq.next() & 0xFFFFFFFFL
        ))
        # Batch event
        self.event_batch.insert({
            "timestamp": timestamp,
            "managed_object": managed_object.id,
            "raw_vars": data,
            "log": [],
            "seq": seq
        })
        self.batched_events += 1

    def on_stream_close(self, stream):
        self.streams.unregister(stream)

    def get_activator_stream(self, name, for_script=False,
                             can_ping=False):
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
            self.blocked_pools.add(name)
            raise Exception("Activator pool '%s' is not available" % name)
        a = self.activators[name]
        if can_ping:
            # Restring to ping operation
            a = [x for x in a if x.can_ping]
        if len(a) == 0:
            self.blocked_pools.add(name)
            raise Exception("No activators in pool '%s' available" % name)
        if not for_script:
            return random.choice(list(a))
        # Weighted balancing
        a = sorted(a, lambda x, y: -cmp(weight(x), weight(y)))[0]
        if a.max_scripts == a.current_scripts:
            self.blocked_pools.add(name)
            raise Exception("All activators are busy in pool '%s'" % name)
        return a

    def script(self, object, script_name, callback, timeout=None, **kwargs):
        """
        Launch a script
        """
        def script_callback(transaction, response=None, error=None):
            if stream is not None:
                stream.current_scripts -= 1
            if object.profile_name != "NOC.SAE":
                try:
                    self.object_scripts[object.id] -= 1
                except KeyError:
                    pass
            if error:
                self.logger.error("script(%s,%s,**%s) failed: %s" % (
                                script_name, object, kwargs, error.text))
                callback(error=error)
                return
            result = response.result
            result = cPickle.loads(str(result))  # De-serialize
            callback(result=result)

        self.logger.info("script %s(%s)" % (script_name, object))
        stream = None
        if object.profile_name != "NOC.SAE":
            # Check object is not unreachable
            if not self.object_status.get(object.id, True):
                # Object is unreachable. Report failure immediately
                e = Error(code=ERR_DOWN, text="Host is down")
                self.logger.error(e.text)
                callback(error=e)
                return
            # Validate activator is present
            try:
                stream = self.get_activator_stream(object.activator.name, True)
            except Exception, why:
                e = Error(code=ERR_ACTIVATOR_NOT_AVAILABLE, text=str(why))
                self.logger.error(e.text)
                callback(error=e)
                return
            # Check object's limits
            o_limits = object.scripts_limit
            if o_limits:
                o_scripts = self.object_scripts.get(object.id, 0)
                if o_scripts >= o_limits:
                    e = Error(code=ERR_OBJ_OVERLOAD,
                              text="Object's script sessions limit exceeded")
                    self.logger.error(e.text)
                    callback(error=e)
                    return
                else:
                    self.object_scripts[object.id] = o_scripts + 1
            # Update counters
            stream.current_scripts += 1
        # Build request
        r = ScriptRequest()
        r.object_name = object.name
        r.script = script_name
        r.access_profile.profile = object.profile_name
        r.access_profile.scheme = object.scheme
        r.access_profile.address = object.address
        credentials = object.credentials
        if object.port:
            r.access_profile.port = object.port
        if credentials.user:
            r.access_profile.user = credentials.user
        if credentials.password:
            r.access_profile.password = credentials.password
        if credentials.super_password:
            r.access_profile.super_password = credentials.super_password
        if object.remote_path:
            r.access_profile.path = object.remote_path
        if credentials.snmp_ro:
            r.access_profile.snmp_ro = credentials.snmp_ro
        if credentials.snmp_rw:
            r.access_profile.snmp_rw = credentials.snmp_rw
        if timeout:
            r.timeout = timeout
        attrs = [(a.key, a.value) for a in object.managedobjectattribute_set.all()]
        for k, v in attrs:
            a = r.access_profile.attrs.add()
            a.key = str(k)
            a.value = v
        for k, v in kwargs.items():
            a = r.kwargs.add()
            a.key = str(k)
            a.value = cPickle.dumps(v)
        # Capabilities
        caps = object.get_caps()
        for c in sorted(caps):
            a = r.access_profile.caps.add()
            a.capability = c
            v = caps[c]
            if isinstance(v, float):
                a.float_value = v
            elif isinstance(v, bool):
                a.bool_value = v
            elif isinstance(v, (int, long)):
                a.int_value = v
            else:
                a.str_value = str(v)
        #
        if object.profile_name == "NOC.SAE":
            self.run_sae_script(r, script_callback)
        else:
            stream.proxy.script(r, script_callback)

    def log_mrt(self, level, task, status, args=None, **kwargs):
        """
        Map/Reduce task logging
        """
        # Log into logfile
        rt = u"-"
        has_task = False
        try:
            if task.task:
                has_task = True
                rt = u"%s" % task.task.id
        except ReduceTask.DoesNotExist:
            if has_task:
                rt = u"?"
        r = [u"MRT task=%s/%d object=%s(%s) script=%s status=%s" % (
                rt, task.id, task.managed_object.name,
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
        self.logger.log(level, u" ".join(r))
        if status == "failed":
            now = datetime.datetime.now()
            FailedScriptLog(
                timestamp=now,
                managed_object=task.managed_object.name,
                address=task.managed_object.address,
                script=task.map_script,
                error_code=kwargs["code"] if "code" in kwargs else None,
                error_text=kwargs["error"],
                expires=now + datetime.timedelta(days=7)
            ).save()
        # Log into mrt log
        # timestamp, map task id, object id, object name, object addres,
        # object profile, script, status
        if self.mrt_log:
            fn = os.path.join(self.mrt_log_dir, str(task.task.id) + ".csv")
            data = [
                time.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                str(task.id),
                str(task.managed_object.id),
                task.managed_object.name.encode("utf-8"),
                task.managed_object.address,
                task.managed_object.profile_name,
                task.map_script,
                status
            ]
            with open(fn, "a") as f:
                w = csv.writer(f)
                w.writerow(data)

    def process_mrtasks(self):
        """
        Process Map/Reduce tasks
        """
        def map_callback(mt_id, result=None, error=None):
            try:
                mt = MapTask.objects.get(id=mt_id)
            except MapTask.DoesNotExist:
                self.logger.error("Late answer for map task %d is ignored" % mt_id)
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
                    variation = 2
                    timeout = random.randint(-timeout / variation,
                                             timeout / variation)
                    next_try = (datetime.datetime.now() +
                                datetime.timedelta(seconds=timeout))
                    if error.code in (ERR_OVERLOAD,
                                      ERR_ACTIVATOR_NOT_AVAILABLE):
                        next_retries = mt.retries_left
                    else:
                        next_retries = mt.retries_left - 1
                    if mt.retries_left and (not mt.task or next_try < mt.task.stop_time):
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
                    timeout=mt.script_timeout,
                    **kwargs)

        def fail_task(mt, code, text):
            mt.status = "F"
            mt.script_result = dict(code=code, text=text)
            try:
                mt.save()
            except Exception:
                pass  # Can raise integrity error if MRT is gone
            self.log_mrt(logging.INFO, task=mt, status="failed",
                code=code, error=text)

        t = datetime.datetime.now()
        # self.logger.debug("Processing MRT schedules")
        # Reset rates
        sae_mrt_rate = 0
        shard_mrt_rate = {}  # shard_id -> count
        throttled_shards = set()  # shard_id
        self.blocked_pools = set()  # Reset block status
        # Run tasks
        qs = {
            "status": "W",
            "next_try__lte": t
        }
        if not self.single_shard:
            qs["managed_object__activator__shard__is_active"] = True
            qs["managed_object__activator__shard__name__in"] = self.shards
        for mt in MapTask.objects.filter(**qs)\
                .order_by("next_try")\
                .select_related("activator", "managed_object")\
                .select_for_update():
            # Check object is managed
            if not mt.managed_object.is_managed:
                fail_task(mt, ERR_OBJECT_NOT_MANAGED, "Object is not managed")
                continue
            # Check reduce task still valid
            is_valid_reduce = True
            try:
                mt.task
            except ReduceTask.DoesNotExist:
                is_valid_reduce = False
            # Check for task timeouts
            if not is_valid_reduce or (mt.task and mt.task.stop_time < t):
                fail_task(mt, ERR_TIMEOUT, text="Timed out")
                continue
            # Check blocked pools
            if mt.managed_object.activator.name in self.blocked_pools:
                # Silently skip task until next round
                self.logger.debug("Delaying task to the blocked pool '%s'" % mt.managed_object.activator.name)
                continue
            # Check for global rate limit
            if self.max_mrt_rate_per_sae:
                if sae_mrt_rate > self.max_mrt_rate_per_sae:
                    self.log_mrt(logging.INFO, task=mt,
                                 status="throttled",
                                 msg="Per-SAE rate limit exceeded "
                                     "(%d)" % self.max_mrt_rate_per_sae)
                    break
                sae_mrt_rate += 1
            # Check for shard rate limit
            if self.max_mrt_rate_per_shard:
                s_id = mt.managed_object.activator.shard.id
                if s_id in throttled_shards:
                    # Shard is throttled, do not log
                    continue
                sr = shard_mrt_rate.get(s_id, 0) + 1
                if sr > self.max_mrt_rate_per_shard:
                    # Log and throttle shard
                    self.log_mrt(logging.INFO, task=mt,
                                 status="throttled",
                                 msg="Per-shard rate limit exceeded "
                                      "(%d)" % self.max_mrt_rate_per_shard)
                    throttled_shards.add(s_id)
                else:
                    shard_mrt_rate[s_id] = sr
            mt.status = "R"
            mt.save()
            exec_script(mt)
        dt = total_seconds(datetime.datetime.now() - t)
        # self.logger.debug("MRT Schedules processed in %ss" % dt)
        if dt > self.mrt_schedule_interval:
            self.logger.error("SAE is overloaded by MRT scheduling (took %ss)" % dt)
            #  @todo: Generate FM event

    def run_sae_script(self, request, callback):
        """
        Run internal SAE script
        """
        kwargs = {}
        for a in request.kwargs:
            kwargs[str(a.key)] = cPickle.loads(str(a.value))
        script = script_registry[request.script](
            profile_registry[request.access_profile.profile],
            self, "SAE", request.access_profile, **kwargs)
        script.sae = self
        with self.script_lock:
            self.script_threads[script] = callback
            self.logger.info("%d script threads" % (len(self.script_threads)))
        script.start()

    def on_script_exit(self, script):
        self.logger.info("Script %s(%s) completed" % (script.name,
                                               script.access_profile.address))
        with self.script_lock:
            cb = self.script_threads.pop(script)
            self.logger.info("%d script threads left" % (len(self.script_threads)))
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

    def map_object(self, object_id):
        """
        Get object by id
        :param object_id: Managed object id
        :type object_id: str
        :return: managed object
        :rtype: ManagedObject or None
        """
        o = self.mo_cache.get(object_id)
        if not o:
            # Not found
            try:
                o = ManagedObject.objects.get(id=int(object_id))
            except ManagedObject.DoesNotExist:
                o = None
            self.mo_cache[object_id] = o
        return o

    def request_activator_status(self, stream):
        """
        Refresh activator statuses
        :return:
        """
        def status_callback(transaction, response=None, error=None):
            if response:
                s = {
                    "timestamp": response.timestamp,
                    "pool": response.pool,
                    "instance": response.instance,
                    "state": response.state,
                    "last_state_change": response.last_state_change,
                    "max_scripts": response.max_scripts,
                    "current_scripts": response.current_scripts,
                    "scripts_processed": response.scripts_processed,
                    "scripts_failed": response.scripts_failed,
                    "scripts": [
                        {
                            "script": i.script,
                            "object_name": i.object_name,
                            "address": i.address,
                            "start_time": i.start_time,
                            "timeout": i.timeout
                        } for i in response.scripts
                    ]
                }
                stream.last_status = s

        stream.proxy.get_status(StatusRequest(), status_callback)

    def refresh_activator_status(self):
        self.logger.debug("Refreshing activator status")
        for pool in self.activators:
            for stream in self.activators[pool]:
                self.request_activator_status(stream)
        self.last_status_refresh = time.time()

    def get_activator_status(self):
        r = []
        for pool in self.activators:
            for stream in self.activators[pool]:
                if hasattr(stream, "last_status"):
                    r += [stream.last_status]
        return r

    def prepare_event_bulk(self):
        self.event_batch = NewEvent._get_collection().initialize_ordered_bulk_op()
        self.batched_events = 0

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
        self.logger.info("STATS:")
        for n, v in s:
            self.logger.info("%s: %s" % (n, v))
        for sock in [s for s in self.factory.sockets.values() if issubclass(s.__class__, RPCSocket)]:
            try:
                self.logger.info("Activator: %s" % self.factory.get_name_by_socket(sock))
            except KeyError:
                self.logger.info("Unregistred activator")
            for n, v in sock.stats:
                self.logger.info("%s: %s" % (n, v))
