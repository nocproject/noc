# ----------------------------------------------------------------------
# Distributed coordinated storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
import time
import orjson
import uuid
from urllib.parse import unquote
import asyncio
from typing import Optional

# Third-party modules
import consul.base

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.comp import smart_text
from noc.core.consul import ConsulClient, ConsulRepeatableErrors
from .base import DCSBase, ResolverBase


class ConsulResolver(ResolverBase):
    async def start(self):
        index = 0
        self.logger.info("[%s] Starting resolver (near=%s)", self.name, self.near)
        while not self.to_shutdown:
            self.logger.debug("[%s] Requesting changes from index %d", self.name, index)
            try:
                old_index = index
                index, services = await self.dcs.consul.health.service(
                    service=self.name,
                    index=index,
                    token=self.dcs.consul_token,
                    passing=True,
                    near=self.near,
                )
            except ConsulRepeatableErrors as e:
                if self.critical:
                    self.dcs.set_faulty_status("Consul error: %s" % e)
                continue
            try:
                index = int(index)
            except ValueError:
                self.logger.error(
                    "[%s] Invalid index format (%r), trying to recover", self.name, index
                )
                index = 0
                continue
            if index > old_index:
                self.logger.debug(
                    "[%s] Index changed %d -> %d. Applying changes", self.name, old_index, index
                )
                r = {
                    str(svc["Service"]["ID"]): "%s:%s"
                    % (
                        str(svc["Service"]["Address"] or svc["Node"]["Address"]),
                        str(svc["Service"]["Port"]),
                    )
                    for svc in services
                }
                self.set_services(r)
            if not self.track:
                break
        self.logger.info("[%s] Stopping resolver", self.name)


class ConsulDCS(DCSBase):
    """
    Consul-based DCS

    URL format:
    consul://<address>[:<port>]/<kv root>?token=<token>&check_interval=<...>&check_timeout=<...>&release_after=<...>
    """

    DEFAULT_CONSUL_HOST = config.consul.host
    DEFAULT_CONSUL_PORT = config.consul.port
    DEFAULT_CONSUL_CHECK_INTERVAL = config.consul.check_interval
    DEFAULT_CONSUL_CHECK_TIMEOUT = config.consul.check_timeout
    DEFAULT_CONSUL_RELEASE = "".join([str(config.consul.release), "s"])
    DEFAULT_CONSUL_SESSION_TTL = config.consul.session_ttl
    DEFAULT_CONSUL_LOCK_DELAY = config.consul.lock_delay
    DEFAULT_CONSUL_RETRY_TIMEOUT = config.consul.retry_timeout
    DEFAULT_CONSUL_KEEPALIVE_ATTEMPTS = config.consul.keepalive_attempts
    EMPTY_HOLDER = ""

    resolver_cls = ConsulResolver

    def __init__(self, runner, url):
        self.name = None
        self.consul_host = self.DEFAULT_CONSUL_HOST
        self.consul_port = self.DEFAULT_CONSUL_PORT
        self.consul_prefix = "/"
        self.consul_token = config.consul.token
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
        super().__init__(runner, url)
        self.consul = ConsulClient(
            host=self.consul_host, port=self.consul_port, token=self.consul_token
        )
        self.session = None
        self.keep_alive_task = None
        self.service_watchers = {}
        self.in_keep_alive = False

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

    async def create_session(self):
        """
        Create consul session
        :return:
        """
        self.logger.info("Creating session")
        checks = ["serfHealth"]
        while True:
            try:
                self.session = await self.consul.session.create(
                    name=self.name,
                    checks=checks,
                    behavior="delete",
                    lock_delay=self.DEFAULT_CONSUL_LOCK_DELAY,
                    ttl=self.DEFAULT_CONSUL_SESSION_TTL,
                )
                break
            except ConsulRepeatableErrors:
                await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                continue
        self.logger.info("Session id: %s", self.session)
        self.keep_alive_task = PeriodicCallback(
            self.keep_alive, self.DEFAULT_CONSUL_SESSION_TTL * 1000 / 2
        )
        self.keep_alive_task.start()

    async def destroy_session(self):
        if self.session:
            self.logger.info("Destroying session %s", self.session)
            if self.keep_alive_task:
                self.keep_alive_task.stop()
                self.keep_alive_task = None
            try:
                await self.consul.session.destroy(self.session)
            except ConsulRepeatableErrors:
                pass  # Ignore consul errors
            self.session = None

    async def register(
        self,
        name,
        address,
        port,
        pool=None,
        lock=None,
        tags=None,
        check_interval: Optional[int] = None,
        check_timeout: Optional[int] = None,
    ):
        if pool:
            name = f"{name}-{pool}"
        self.name = name
        if lock:
            await self.acquire_lock(lock)
        svc_id = self.session or str("svc-%s" % uuid.uuid4())
        tags = tags[:] if tags else []
        tags += [svc_id]
        self.svc_check_url = f"http://{address}:{port}/health/?service={svc_id}"
        self.health_check_service_id = svc_id
        if config.features.consul_healthchecks:
            checks = consul.Check.http(
                self.svc_check_url,
                f"{check_interval or self.check_interval}s",
                f"{check_timeout or self.check_timeout}s",
            )
            checks["DeregisterCriticalServiceAfter"] = self.release_after
        else:
            checks = []
        if config.features.service_registration:
            while True:
                self.logger.info(
                    "Registering service %s: %s:%s (id=%s)", name, address, port, svc_id
                )
                try:
                    r = await self.consul.agent.service.register(
                        name=name,
                        service_id=svc_id,
                        address=address,
                        port=port,
                        tags=tags,
                        check=checks,
                    )
                except ConsulRepeatableErrors as e:
                    metrics["error", ("type", "cant_register_consul")] += 1
                    self.logger.info("Cannot register service %s: %s", name, e)
                    await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                    continue
                if r:
                    self.svc_id = svc_id
                break
            return r
        else:
            return True

    async def deregister(self):
        if self.session:
            try:
                await self.destroy_session()
            except ConsulRepeatableErrors:
                metrics["error", ("type", "cant_destroy_consul_session_soft")] += 1
            except Exception as e:
                metrics["error", ("type", "cant_destroy_consul_session")] += 1
                self.logger.error("Cannot destroy session: %s", e)
        if self.svc_id and config.features.service_registration:
            try:
                await self.consul.agent.service.deregister(self.svc_id)
            except ConsulRepeatableErrors:
                metrics["error", ("type", "cant_deregister_consul_soft")] += 1
            except Exception as e:
                metrics["error", ("type", "cant_deregister_consul")] += 1
                self.logger.error("Cannot deregister service: %s", e)
            self.svc_id = None

    async def keep_alive(self):
        metrics["dcs_consul_keepalives"] += 1
        if self.in_keep_alive:
            metrics["error", ("type", "dcs_consul_overlapped_keepalives")] += 1
            return
        self.in_keep_alive = True
        try:
            if self.session:
                touched = False
                for n in range(self.keepalive_attempts):
                    try:
                        await self.consul.session.renew(self.session)
                        self.logger.debug("Session renewed")
                        touched = True
                        break
                    except consul.base.NotFound as e:
                        self.logger.warning("Session lost by: '%s'. Forcing quit", e)
                        break
                    except ConsulRepeatableErrors as e:
                        self.logger.warning("Cannot refresh session due to ignorable error: %s", e)
                        metrics["error", ("type", "dcs_consul_keepalive_retries")] += 1
                        await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                if not touched:
                    self.logger.critical("Cannot refresh session, stopping")
                    if self.keep_alive_task:
                        self.keep_alive_task.stop()
                        self.keep_alive_task = None
                    self.kill()
            elif self.keep_alive_task:
                self.keep_alive_task.stop()
                self.keep_alive_task = None
        finally:
            self.in_keep_alive = False

    def get_lock_path(self, lock):
        return self.consul_prefix + "/locks/" + lock

    async def acquire_lock(self, name):
        if not self.session:
            await self.create_session()
        key = self.get_lock_path(name)
        index = None
        while True:
            self.logger.info("Acquiring lock: %s", key)
            try:
                status = await self.consul.kv.put(
                    key=key, value=self.session, acquire=self.session, token=self.consul_token
                )
                if status:
                    break
                else:
                    metrics["error", ("type", "dcs_consul_failed_get_lock")] += 1
                    self.logger.info("Failed to acquire lock")
                    await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
            except ConsulRepeatableErrors:
                await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                continue
            # Waiting for lock release
            while True:
                try:
                    index, data = await self.consul.kv.get(
                        key=key, index=index, token=self.consul_token
                    )
                    if not data:
                        index = None  # Key has been deleted
                        await asyncio.sleep(
                            self.DEFAULT_CONSUL_LOCK_DELAY * (0.5 + random.random())
                        )
                    break
                except ConsulRepeatableErrors:
                    await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
        self.logger.info("Lock acquired")

    def _get_manifest_path(self, name: str) -> str:
        """
        Get manifest path.

        Args:
            name: Service name.

        Returns:
            manifest path.
        """
        return f"{self.consul_prefix}/slots/{name}/manifest"

    async def get_slot_limit(self, name: str) -> Optional[int]:
        """
        Return the current limit for given slot
        :param name:
        :return:
        """
        manifest_path = self._get_manifest_path(name)
        while True:
            self.logger.info("Attempting to get slot")
            # Non-blocking for a first time
            # Block until change every next try
            try:
                _, cv = await self.consul.kv.get(key=manifest_path, index=0)
                if not cv:
                    return 0
                return int(orjson.loads(cv["Value"]).get("Limit", 0))
            except ConsulRepeatableErrors:
                await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)

    async def set_slot_limit(self, name: str, limit: int) -> None:
        manifest_path = self._get_manifest_path(name)
        while True:
            try:
                if limit > 0:
                    self.logger.info("Setting slots for %s = %s", name, limit)
                    await self.consul.kv.put(
                        key=manifest_path, value=orjson.dumps({"Limit": limit}).decode()
                    )
                    return
                else:
                    self.logger.info("Deleting slots for %s", name)
                    await self.consul.kv.delete(key=manifest_path)
                    return
            except ConsulRepeatableErrors:
                await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)

    async def acquire_slot(self, name, limit):
        """
        Acquire shard slot
        :param name: <service name>-<pool>
        :param limit: Configured limit
        :return: (slot number, number of instances)
        """
        if not self.session:
            await self.create_session()
        if self.total_slots is not None:
            return self.slot_number, self.total_slots
        prefix = "%s/slots/%s" % (self.consul_prefix, name)
        contender_path = "%s/%s" % (prefix, self.session)
        contender_info = self.session
        manifest_path = "%s/manifest" % prefix
        self.logger.info("Writing contender slot info into %s", contender_path)
        while True:
            try:
                status = await self.consul.kv.put(
                    key=contender_path,
                    value=contender_info,
                    acquire=self.session,
                    token=self.consul_token,
                )
                if status:
                    break
                else:
                    metrics["error", ("type", "dcs_consul_failed_get_slot")] += 1
                    self.logger.info("Failed to write contender slot info")
                    await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
            except ConsulRepeatableErrors:
                await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
        index = 0
        cas = 0
        while True:
            self.logger.info("Attempting to get slot")
            seen_sessions = set()
            dead_contenders = set()
            manifest = None
            # Non-blocking for a first time
            # Block until change every next try
            try:
                index, cv = await self.consul.kv.get(key=prefix, index=index, recurse=True)
            except ConsulRepeatableErrors:
                await asyncio.sleep(self.DEFAULT_CONSUL_RETRY_TIMEOUT)
                continue
            for e in cv:
                if e["Key"] == manifest_path:
                    cas = e["ModifyIndex"]
                    # @todo: Handle errors
                    manifest = orjson.loads(e["Value"])
                elif "Session" in e:
                    seen_sessions.add(e["Session"])
                else:
                    dead_contenders.add(e["Key"])
            if manifest:
                total_slots = int(manifest.get("Limit", 0))
                holders = [
                    h if h in seen_sessions else self.EMPTY_HOLDER
                    for h in manifest.get("Holders", [])
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
            self.logger.info("Attempting to acquire slot %s/%s", slot_number, total_slots)
            try:
                r = await self.consul.kv.put(
                    key=manifest_path,
                    value=smart_text(
                        orjson.dumps(
                            {"Limit": total_slots, "Holders": holders}, option=orjson.OPT_INDENT_2
                        ).decode()
                    ),
                    cas=cas,
                )
            except ConsulRepeatableErrors as e:
                self.logger.info("Cannot acquire slot: %s", e)
                continue
            if r:
                self.logger.info("Acquired slot %s/%s", slot_number, total_slots)
                self.slot_number = slot_number
                self.total_slots = total_slots
                return slot_number, total_slots
            self.logger.info("Cannot acquire slot: CAS changed, retry")

    async def resolve_near(
        self, name, hint=None, wait=True, timeout=None, full_result=False, critical=False
    ):
        """
        Synchronous call to resolve nearby service
        Commonly used for external services like databases
        :param name: Service name
        :param wait:
        :param timeout:
        :param full_result:
        :param hint:
        :param critical:
        :return: address:port
        """
        self.logger.info("Resolve near service %s", name)
        index = 0
        while True:
            try:
                index, services = await self.consul.health.service(
                    service=name, index=index, near="_agent", token=self.consul_token, passing=True
                )
            except ConsulRepeatableErrors as e:
                metrics["error", ("type", "dcs_consul_failed_resolve_near")] += 1
                self.logger.info("Consul error: %s", e)
                if critical:
                    metrics["error", ("type", "dcs_consul_failed_resolve_critical_near")] += 1
                    self.set_faulty_status("Consul error: %s" % e)
                time.sleep(config.consul.near_retry_timeout)
                continue
            if not services and wait:
                metrics["error", ("type", "dcs_consul_no_active_service %s" % name)] += 1
                self.logger.info("No active service %s. Waiting", name)
                if critical:
                    metrics[
                        "error", ("type", "dcs_consul_no_active_critical_service %s" % name)
                    ] += 1
                    self.set_faulty_status("No active service %s. Waiting" % name)
                time.sleep(config.consul.near_retry_timeout)
                continue
            r = []
            for svc in services:
                r += [
                    "%s:%s"
                    % (
                        str(svc["Service"]["Address"] or svc["Node"]["Address"]),
                        str(svc["Service"]["Port"]),
                    )
                ]
                if not full_result:
                    break
            self.logger.info("Resolved near service %s to %s", name, r)
            if critical:
                self.clear_faulty_status()
            return r
