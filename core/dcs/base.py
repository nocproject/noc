# ----------------------------------------------------------------------
# Distributed coordinated storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import random
import signal
import threading
import os
from urllib.parse import urlparse
from time import perf_counter
import asyncio
from typing import Optional

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.ioloop.util import run_sync
from noc.core.ioloop.timers import PeriodicCallback
from .error import ResolutionError


class DCSBase(object):
    # Resolver class
    resolver_cls = None
    # HTTP code to be returned by /health endpoint when service is healthy
    HEALTH_OK_HTTP_CODE = 200
    # HTTP code to be returned by /health endpoint when service is unhealthy
    # and must be temporary removed from resolver
    HEALTH_FAILED_HTTP_CODE = 429

    def __init__(self, runner, url):
        self.runner = runner
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.parse_url(urlparse(url))
        # service -> resolver instances
        self.resolvers = {}
        self.resolvers_lock = threading.Lock()
        self.resolver_expiration_task = None
        self.health_check_service_id = None
        self.status = True
        self.status_message = ""
        self.thread_id = None

    def parse_url(self, u):
        pass

    async def start(self):
        """
        Start all pending tasks
        :return:
        """
        self.thread_id = threading.get_ident()
        self.resolver_expiration_task = PeriodicCallback(self.expire_resolvers, 10000)
        self.resolver_expiration_task.start()

    def stop(self):
        """
        Stop all pending tasks
        :return:
        """
        if self.resolver_expiration_task:
            self.resolver_expiration_task.stop()
            self.resolver_expiration_task = None
        # Stop all resolvers
        with self.resolvers_lock:
            for svc in self.resolvers:
                r = self.resolvers[svc]
                self.logger.info("Stopping resolver for service %s", svc)
                r.stop()
            self.resolvers = {}

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
        """
        Register service
        :param name:
        :param address:
        :param port:
        :param pool:
        :param lock:
        :param tags: List of extra tags
        :param check_interval: DCS Check Interval
        :param check_timeout: DCS Check Timeout
        :return:
        """
        raise NotImplementedError()

    def kill(self):
        self.logger.info("Shooting self with SIGTERM")
        os.kill(os.getpid(), signal.SIGTERM)

    async def get_slot_limit(self, name: str) -> Optional[int]:
        """
        Return the current limit for given slot
        :param name:
        :return:
        """
        raise NotImplementedError()

    async def set_slot_limit(self, name: str, limit: int) -> None:
        """
        Set limits for given slot.

        Remove slot if limit is zero.

        Args:
            name: Slot name.
            limit: New limit.
        """
        raise NotImplementedError()

    async def acquire_slot(self, name, limit):
        """
        Acquire shard slot
        :param name: <service name>-<pool>
        :param limit: Configured limit
        :return: (slot number, number of instances)
        """
        raise NotImplementedError()

    async def get_resolver(self, name, critical=False, near=False, track=True):
        def run_resolver(res):
            loop = asyncio.get_running_loop()
            loop.call_soon(loop.create_task, res.start())

        if track:
            with self.resolvers_lock:
                resolver = self.resolvers.get((name, critical, near))
                if not resolver:
                    self.logger.info("Running resolver for service %s", name)
                    resolver = self.resolver_cls(self, name, critical=critical, near=near)
                    self.resolvers[name, critical, near] = resolver
                    run_resolver(resolver)
        else:
            # One-time resolver
            resolver = self.resolver_cls(self, name, critical=critical, near=near, track=False)
            run_resolver(resolver)
        return resolver

    async def resolve(
        self,
        name,
        hint=None,
        wait=True,
        timeout=None,
        full_result=False,
        critical=False,
        near=False,
        track=True,
    ):
        async def wrap():
            resolver = await self.get_resolver(name, critical=critical, near=near, track=track)
            r = await resolver.resolve(
                hint=hint, wait=wait, timeout=timeout, full_result=full_result
            )
            return r

        return await self.runner.trampoline(wrap())

    async def expire_resolvers(self):
        with self.resolvers_lock:
            for svc in list(self.resolvers):
                r = self.resolvers[svc]
                if r.is_expired():
                    self.logger.info("Stopping expired resolver for service %s", svc)
                    r.stop()
                    del self.resolvers[svc]

    def resolve_sync(self, name, hint=None, wait=True, timeout=None, full_result=False):
        """
        Returns *hint* when service is active or new service
        instance,
        :param name:
        :param hint:
        :param full_result:
        :return:
        """

        async def _resolve():
            r = await self.resolve(
                name, hint=hint, wait=wait, timeout=timeout, full_result=full_result
            )
            return r

        return run_sync(_resolve)

    async def resolve_near(
        self, name, hint=None, wait=True, timeout=None, full_result=False, critical=False
    ):
        """
        Synchronous call to resolve nearby service
        Commonly used for external services like databases
        :param name: Service name
        :return: address:port
        """
        raise NotImplementedError()

    def get_status(self):
        if self.status:
            return self.HEALTH_OK_HTTP_CODE, "OK"
        else:
            return self.HEALTH_FAILED_HTTP_CODE, self.status_message

    def set_faulty_status(self, message):
        if self.status or self.status_message != message:
            self.logger.info("Set faulty status to: %s", message)
            self.status = False
            self.status_message = message

    def clear_faulty_status(self):
        if not self.status:
            self.logger.info("Clearing faulty status")
            self.status = True
            self.status_message = ""


class ResolverBase(object):
    def __init__(self, dcs, name, critical=False, near=False, track=True):
        self.dcs = dcs
        self.name = name
        self.to_shutdown = False
        self.logger = self.dcs.logger
        self.services = {}
        self.service_ids = []
        self.service_addresses = set()
        self.lock = threading.Lock()
        self.policy = self.policy_random
        self.rr_index = -1
        self.critical = critical
        self.near = near
        self.is_ready = False
        self.thread_id = threading.get_ident()
        self.ready_event_async = asyncio.Event()
        self.ready_event_sync = threading.Event()
        self.track = track
        self.last_used = perf_counter()

    def stop(self):
        self.to_shutdown = True
        metrics["dcs_resolver_activeservices", ("name", self.name)] = 0

    async def start(self):
        raise NotImplementedError()

    def set_services(self, services):
        """
        Update actual list of services
        :param services: dict of service_id -> <address>:<port>
        :return:
        """
        if self.to_shutdown:
            return
        with self.lock:
            if self.critical:
                if services:
                    self.dcs.clear_faulty_status()
                else:
                    self.dcs.set_faulty_status("No active services %s" % self.name)
            self.services = services
            self.service_ids = sorted(services.keys())
            self.service_addresses = set(services.values())
            if self.services:
                self.logger.info(
                    "[%s] Set active services to: %s",
                    self.name,
                    ", ".join("%s: %s" % (i, self.services[i]) for i in self.services),
                )
                self.set_ready()
            else:
                self.logger.info("[%s] No active services", self.name)
                self.clear_ready()
            metrics["dcs_resolver_activeservices", ("name", self.name)] = len(self.services)

    def set_ready(self):
        self.is_ready = True
        self.ready_event_async.set()
        self.ready_event_sync.set()

    def clear_ready(self):
        self.is_ready = False
        self.ready_event_async.clear()
        self.ready_event_sync.clear()

    def is_same_thread(self):
        return self.thread_id == threading.get_ident()

    async def _wait_for_services_async(self, timeout):
        try:
            await asyncio.wait_for(
                self.ready_event_async.wait(), timeout or config.dcs.resolution_timeout
            )
        except asyncio.TimeoutError:
            metrics["errors", ("type", "dcs_resolver_timeout")] += 1
            if self.critical:
                self.dcs.set_faulty_status("Failed to resolve %s: Timeout" % self.name)
            raise ResolutionError()

    def _wait_for_services_sync(self, timeout):
        if not self.ready_event_sync.wait(timeout):
            metrics["errors", ("type", "dcs_resolver_timeout")] += 1
            if self.critical:
                self.dcs.set_faulty_status("Failed to resolve %s: Timeout" % self.name)
            raise ResolutionError()

    async def _wait_for_services(self, timeout=None):
        if self.is_same_thread():
            await self._wait_for_services_async(timeout)
        else:
            self._wait_for_services_sync(timeout)

    async def resolve(self, hint=None, wait=True, timeout=None, full_result=False):
        self.last_used = perf_counter()
        metrics["dcs_resolver_requests"] += 1
        if not self.services and wait:
            # Wait until service catalog populated
            await self._wait_for_services(timeout)
        if not wait and not self.is_ready:
            if self.critical:
                self.dcs.set_faulty_status("Failed to resolve %s: No active services" % self.name)
            raise ResolutionError()
        with self.lock:
            if hint and hint in self.service_addresses:
                location = hint
                metrics["dcs_resolver_hints"] += 1
            elif full_result:
                location = list(self.services.values())
            else:
                location = self.services[self.policy()]
        metrics["dcs_resolver_success"] += 1
        if self.critical:
            self.dcs.clear_faulty_status()
        return location

    def policy_random(self):
        """
        Randomly select service
        :return:
        """
        return random.choice(self.service_ids)

    def policy_rr(self):
        """
        Round-robin selection of service
        :return:
        """
        self.rr_index = min(self.rr_index + 1, len(self.service_ids) - 1)
        return self.service_ids[self.rr_index]

    def is_expired(self) -> bool:
        """
        Check if resolver is no longer used and may be expired
        :return:
        """
        return perf_counter() - self.last_used > config.dcs.resolver_expiration_timeout
