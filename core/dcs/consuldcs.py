# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Distributed coordinated storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import uuid
import random
## Third-party modules
from six.moves.urllib.parse import unquote
import tornado.gen
import tornado.ioloop
import consul.base
import consul.tornado
import ujson
## NOC modules
from base import DCSBase, ResolverBase

ConsulRepeatableErrors = consul.base.Timeout


class ConsulResolver(ResolverBase):
    @tornado.gen.coroutine
    def start(self):
        index = 0
        self.logger.info("[%s] Starting resolver", self.name)
        while not self.to_shutdown:
            try:
                index, services = yield self.dcs.consul.catalog.service(
                    service=self.name,
                    index=index,
                    token=self.dcs.consul_token
                )
            except ConsulRepeatableErrors:
                continue
            r = dict(
                (svc["ID"], "%s:%s" % (svc["ServiceAddress"], svc["ServicePort"]))
                for svc in services
            )
            self.set_services(r)
        self.logger.info("[%s] Stopping resolver", self.name)


class ConsulDCS(DCSBase):
    """
    Consul-based DCS
    
    URL format:
    consul://<address>[:<port>]/<kv root>?token=<token>&check_interval=<...>&check_timeout=<...>&release_after=<...>
    """
    DEFAULT_CONSUL_HOST = "consul"
    DEFAULT_CONSUL_PORT = 8500
    DEFAULT_CONSUL_CHECK_INTERVAL = 1
    DEFAULT_CONSUL_CHECK_TIMEOUT = 1
    DEFAULT_CONSUL_RELEASE = "1m"
    DEFAULT_CONSUL_SESSION_TTL = 10
    DEFAULT_CONSUL_LOCK_DELAY = 1
    DEFAULT_CONSUL_RETRY_TIMEOUT = 1
    DEFAULT_CONSUL_KEEPALIVE_ATTEMPTS = 5
    EMPTY_HOLDER = ""

    resolver_cls = ConsulResolver

    def __init__(self, url, ioloop=None):
        self.name = None
        self.consul_host = self.DEFAULT_CONSUL_HOST
        self.consul_port = self.DEFAULT_CONSUL_PORT
        self.consul_prefix = "/"
        self.consul_token = None
        self.check_interval = self.DEFAULT_CONSUL_CHECK_INTERVAL
        self.check_timeout = self.DEFAULT_CONSUL_CHECK_TIMEOUT
        self.release_after = self.DEFAULT_CONSUL_RELEASE
        self.keepalive_attempts = self.DEFAULT_CONSUL_KEEPALIVE_ATTEMPTS
        self.svc_name = None
        self.svc_address = None
        self.svc_port = None
        self.svc_check_url = None
        self.svc_id = None
        self.session = None
        self.slot_number = None
        self.total_slots = None
        super(ConsulDCS, self).__init__(url, ioloop)
        self.consul = consul.tornado.Consul(
            host=self.consul_host,
            port=self.consul_port,
            token=self.consul_token
        )
        self.session = None
        self.keep_alive_task = None
        self.service_watchers = {}

    def parse_url(self, u):
        if ":" in u.netloc:
            self.consul_host, port = u.netloc.rsplit(":", 1)
            self.consul_port = int(port)
        else:
            self.consul_host = u.netloc
        self.consul_prefix = u.path[1:]
        if self.consul_prefix.endswith("/"):
            self.consul_prefix = self.consul_prefix[:-1]
        for q in u.query.split("&"):
            if not q or "=" not in q:
                continue
            k, v = q.split("=", 1)
            v = unquote(v)
            if k == "token":
                self.consul_token = v
            elif k == "check_interval":
                self.check_interval = int(v)
            elif k == "check_timeout":
                self.check_timeout = int(v)
            elif k == "release_after":
                self.release_after = v

    @tornado.gen.coroutine
    def create_session(self):
        """
        Create consul session
        :return: 
        """
        self.logger.info("Creating session")
        # @todo: Add http healthcheck
        checks = ["serfHealth"]
        while True:
            try:
                self.session = yield self.consul.session.create(
                    name=self.name,
                    checks=checks,
                    behavior="delete",
                    lock_delay=1,
                    ttl=self.DEFAULT_CONSUL_SESSION_TTL
                )
                break
            except ConsulRepeatableErrors:
                yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                continue
        self.logger.info("Session id: %s", self.session)
        self.keep_alive_task = tornado.ioloop.PeriodicCallback(
            self.keep_alive,
            self.DEFAULT_CONSUL_SESSION_TTL * 1000 / 2,
            self.ioloop
        )
        self.keep_alive_task.start()

    @tornado.gen.coroutine
    def destroy_session(self):
        if self.session:
            self.logger.info("Destroying session %s", self.session)
            if self.keep_alive_task:
                self.keep_alive_task.stop()
                self.keep_alive_task = None
            try:
                yield self.consul.session.destroy(self.session)
            except ConsulRepeatableErrors:
                pass  # Ignore consul errors
            self.session = None

    @tornado.gen.coroutine
    def register(self, name, address, port, lock=None):
        self.name = name
        self.svc_check_url = "http://%s:%s/health/" % (address, port)
        if lock:
            yield self.acquire_lock(lock)
        svc_id = self.session or str(uuid.uuid4())
        checks = consul.Check.http(
            self.svc_check_url,
            self.check_interval,
            "%ds" % self.check_timeout
        )
        checks["DeregisterCriticalServiceAfter"] = self.release_after
        while True:
            self.logger.info("Registering service %s: %s:%s (id=%s)",
                             name, address, port, svc_id)
            try:
                r = yield self.consul.agent.service.register(
                    name=name,
                    service_id=svc_id,
                    address=address,
                    port=port,
                    tags=[svc_id],
                    check=checks
                )
            except ConsulRepeatableErrors:
                yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                continue
            if r:
                self.svc_id = svc_id
            break
        raise tornado.gen.Return(r)

    @tornado.gen.coroutine
    def deregister(self):
        if self.session:
            try:
                yield self.destroy_session()
            except ConsulRepeatableErrors:
                pass
        if self.svc_id:
            try:
                yield self.consul.agent.service.deregister(self.svc_id)
            except ConsulRepeatableErrors:
                pass
            self.svc_id = None

    @tornado.gen.coroutine
    def keep_alive(self):
        if self.session:
            touched = False
            for n in range(self.keepalive_attempts):
                try:
                    yield self.consul.session.renew(self.session)
                    touched = True
                    break
                except consul.base.NotFound:
                    self.logger.info("Session lost. Forcing quit")
                    break
                except ConsulRepeatableErrors as e:
                    self.logger.info("Cannot refresh session due to ignorable error: %s", e)
                    yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
            if not touched:
                self.logger.info("Cannot refresh session, stopping")
                self.keep_alive_task.stop()
                self.keep_alive_task = None
                self.kill()
        else:
            self.keep_alive_task.stop()
            self.keep_alive_task = None

    def get_lock_path(self, lock):
        return self.consul_prefix + "/locks/" + lock

    @tornado.gen.coroutine
    def acquire_lock(self, name):
        if not self.session:
            yield self.create_session()
        key = self.get_lock_path(name)
        index = None
        while True:
            self.logger.info("Acquiring lock: %s", key)
            try:
                status = yield self.consul.kv.put(
                    key=key,
                    value=self.session,
                    acquire=self.session,
                    token=self.consul_token
                )
                if status:
                    break
                else:
                    self.logger.info("Failed to acquire lock")
                    yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
            except ConsulRepeatableErrors:
                yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                continue
            # Waiting for lock release
            while True:
                try:
                    index, data = yield self.consul.kv.get(
                        key=key,
                        index=index,
                        token=self.consul_token
                    )
                    if not data:
                        index = None  # Key has been deleted
                        yield tornado.gen.sleep(
                            self.DEFAULT_CONSUL_LOCK_DELAY * (0.5 + random.random())
                        )
                    break
                except ConsulRepeatableErrors:
                    yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
        self.logger.info("Lock acquired")

    @tornado.gen.coroutine
    def acquire_slot(self, name, limit):
        """
        Acquire shard slot
        :param name: <service name>-<pool>
        :param limit: Configured limit
        :return: (slot number, number of instances) 
        """
        if not self.session:
            yield self.create_session()
        if self.total_slots is not None:
            raise tornado.gen.Return(
                (self.slot_number, self.total_slots)
            )
        prefix = "%s/slots/%s" % (self.consul_prefix, name)
        contender_path = "%s/%s" % (prefix, self.session)
        contender_info = self.session
        manifest_path = "%s/manifest" % prefix
        self.logger.info("Writing contender slot info into %s", contender_path)
        while True:
            try:
                status = yield self.consul.kv.put(
                    key=contender_path,
                    value=contender_info,
                    acquire=self.session,
                    token=self.consul_token
                )
                if status:
                    break
                else:
                    self.logger.info("Failed to write contender slot info")
                    yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
            except ConsulRepeatableErrors:
                yield tornado.gen.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
        index = 0
        cas = 0
        while True:
            self.logger.info("Attempting to get slot")
            seen_sessions = set()
            dead_contenders = set()
            manifest = None
            # Non-blocking for a first time
            # Block until change every next try
            index, cv = yield self.consul.kv.get(
                key=prefix, index=index, recurse=True
            )
            for e in cv:
                if e["Key"] == manifest_path:
                    cas = e["ModifyIndex"]
                    # @todo: Handle errors
                    manifest = ujson.loads(e["Value"])
                else:
                    if "Session" in e:
                        seen_sessions.add(e["Session"])
                    else:
                        dead_contenders.add(e["Key"])
            if manifest:
                total_slots = manifest["Limit"]
                holders = [
                    h if h in seen_sessions else self.EMPTY_HOLDER
                    for h in manifest["Holders"]
                ]
            else:
                self.logger.info("Initializing manifest")
                total_slots = limit
                holders = []
            # Try to allocate slot
            if len(holders) < total_slots:
                # Available slots from the end
                slot_number = len(holders)
                holders += [self.session]
            else:
                # Try to reclaim slots in the middle
                try:
                    slot_number = holders.index(self.EMPTY_HOLDER)
                    holders[slot_number] = self.session
                except ValueError:
                    self.logger.info("All slots a busy, waiting")
                    continue
            # Update manifest
            self.logger.info("Attempting to acquire slot %s/%s",
                             slot_number, total_slots)
            try:
                r = yield self.consul.kv.put(
                    key=manifest_path,
                    value=ujson.dumps({
                        "Limit": total_slots,
                        "Holders": holders
                    }),
                    cas=cas
                )
            except ConsulRepeatableErrors as e:
                self.logger.info("Cannot acquire slot: %s", e)
                continue
            if r:
                self.logger.info("Acquired slot %s/%s",
                                 slot_number, total_slots)
                self.slot_number = slot_number
                self.total_slots = total_slots
                raise tornado.gen.Return((slot_number, total_slots))
            self.logger.info("Cannot acquire slot: CAS changed, retry")
