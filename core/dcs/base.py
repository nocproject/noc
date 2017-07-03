# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Distributed coordinated storage
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import signal
import os
from threading import Lock
import random
import datetime
import Queue
# Third-party modules
import tornado.gen
import tornado.locks
import tornado.ioloop
from six.moves.urllib.parse import urlparse
# Python modules
from noc.core.perf import metrics


class ResolutionError(Exception):
    pass


class DCSBase(object):
    DEFAULT_SERVICE_RESOLUTION_TIMEOUT = datetime.timedelta(seconds=300)
    # Resolver class
    resolver_cls = None

    def __init__(self, url, ioloop=None):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.ioloop = ioloop or tornado.ioloop.IOLoop.current()
        self.parse_url(urlparse(url))
        # service -> resolver instances
        self.resolvers = {}
        self.resolvers_lock = Lock()
        self.resolver_expiration_task = tornado.ioloop.PeriodicCallback(
            self.expire_resolvers,
            10000
        )
        self.health_check_service_id = None

    def parse_url(self, u):
        pass

    def start(self):
        """
        Run IOLoop if not started yet
        :return:
        """
        self.resolver_expiration_task.start()
        self.ioloop.start()

    def stop(self):
        """
        Stop IOLoop if not stopped yet
        :return:
        """
        self.resolver_expiration_task.stop()
        self.ioloop.stop()

    @tornado.gen.coroutine
    def register(self, name, address, port, pool=None, lock=None, tags=None):
        """
        Register service
        :param name:
        :param address:
        :param port:
        :param pool:
        :param lock:
        :param tags: List of extra tags
        :return:
        """
        raise NotImplementedError()

    def kill(self):
        self.logger.info("Shooting self with SIGTERM")
        os.kill(os.getpid(), signal.SIGTERM)

    @tornado.gen.coroutine
    def acquire_slot(self, name, limit):
        """
        Acquire shard slot
        :param name: <service name>-<pool>
        :param limit: Configured limit
        :return: (slot number, number of instances)
        """
        raise NotImplementedError()

    @tornado.gen.coroutine
    def get_resolver(self, name):
        with self.resolvers_lock:
            resolver = self.resolvers.get(name)
            if not resolver:
                self.logger.info("Running resolver for service %s", name)
                resolver = self.resolver_cls(self, name)
                self.resolvers[name] = resolver
                self.ioloop.add_callback(resolver.start)
        raise tornado.gen.Return(resolver)

    @tornado.gen.coroutine
    def resolve(self, name, hint=None):
        resolver = yield self.get_resolver(name)
        r = yield resolver.resolve(hint=hint)
        raise tornado.gen.Return(r)

    @tornado.gen.coroutine
    def expire_resolvers(self):
        with self.resolvers_lock:
            for svc in self.resolvers:
                r = self.resolvers[svc]
                if r.is_expired():
                    self.logger.info("Stopping expired resolver for service %s", svc)
                    r.stop()
                    del self.resolvers[svc]

    @tornado.gen.coroutine
    def _resolve_sync(self, queue, name, hint=None):
        try:
            result = yield self.resolve(name, hint=hint)
            queue.put(result)
        except tornado.gen.Return as e:
            queue.put(e.value)
        except Exception as e:
            queue.put(e)

    def resolve_sync(self, name, hint=None):
        """
        Returns *hint* when service is active or new service
        instance,
        :param name:
        :param hint:
        :return:
        """
        q = Queue.Queue()
        self.ioloop.add_callback(self._resolve_sync, q, name, hint)
        result = q.get()
        if isinstance(result, Exception):
            raise result
        else:
            return result

    def resolve_near(self, name):
        """
        Synchronous call to resolve nearby service
        Commonly used for external services like databases
        :param name: Service name
        :return: address:port
        """
        raise NotImplementedError()


class ResolverBase(object):
    def __init__(self, dcs, name):
        self.dcs = dcs
        self.name = name
        self.to_shutdown = False
        self.logger = self.dcs.logger
        self.services = {}
        self.service_ids = []
        self.service_addresses = set()
        self.lock = Lock()
        self.policy = self.policy_random
        self.rr_index = -1
        self.ready_event = tornado.locks.Event()

    def stop(self):
        self.to_shutdown = True
        metrics["dcs.resolver.%s.activeservices" % self.name] = 0

    @tornado.gen.coroutine
    def start(self):
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
            self.services = services
            self.service_ids = sorted(services.keys())
            self.service_addresses = set(services.values())
            if self.services:
                self.logger.info(
                    "[%s] Set active services to: %s",
                    self.name,
                    ", ".join("%s: %s" % (i, self.services[i])
                              for i in self.services))
                self.ready_event.set()
            else:
                self.logger.info("[%s] No active services", self.name)
                self.ready_event.clear()
            metrics["dcs.resolver.%s.activeservices" % self.name] = len(self.services)

    @tornado.gen.coroutine
    def resolve(self, hint=None):
        metrics["dcs.resolver.requests"] += 1
        # Wait until service catalog populated
        try:
            yield self.ready_event.wait(timeout=self.dcs.DEFAULT_SERVICE_RESOLUTION_TIMEOUT)
        except tornado.gen.TimeoutError:
            metrics["dcs.resolver.errors"] += 1
            raise ResolutionError()
        with self.lock:
            if hint and hint in self.service_addresses:
                location = hint
                metrics["dcs.resolver.hints"] += 1
            else:
                location = self.services[self.policy()]
        metrics["dcs.resolver.success"] += 1
        raise tornado.gen.Return(location)

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
