# ----------------------------------------------------------------------
# Base service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import sys
import logging
import signal
import uuid
import argparse
import threading
import random
from time import perf_counter
import asyncio
import cachetools
from functools import partial
from typing import (
    Optional,
    Dict,
    List,
    Tuple,
    Callable,
    Any,
    TypeVar,
    NoReturn,
    Awaitable,
    Iterable,
)

# Third-party modules
import setproctitle

# NOC modules
from noc.config import config
from noc.core.debug import excepthook, error_report
from noc.core.log import ErrorFormatter
from noc.core.perf import apply_metrics
from noc.core.hist.monitor import apply_hists
from noc.core.quantile.monitor import apply_quantiles
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from noc.core.threadpool import ThreadPoolExecutor
from noc.core.span import get_spans, span_to_dict
from noc.core.tz import setup_timezone
from noc.core.msgstream.client import MessageStreamClient
from noc.core.msgstream.queue import MessageStreamQueue
from noc.core.msgstream.queuebuffer import QBuffer
from noc.core.msgstream.message import Message
from noc.core.msgstream.error import MsgStreamError
from noc.core.router.base import Router
from noc.core.router.messagebuffer import MBuffer
from noc.core.ioloop.util import setup_asyncio
from noc.core.ioloop.timers import PeriodicCallback
from noc.core.error import NOCError
from noc.core.mx import MX_STREAM, MX_SPAN_CTX, MX_SPAN_ID
from noc.core.span import Span
from .rpc import RPCProxy
from .loader import set_service
from ..router.datastream import RouteDataStreamClient

T = TypeVar("T")


class BaseService(object):
    """
    Basic service implementation.

    * on_change_<var> - subscribed to changes of config variable <var>
    """

    # Service name
    name = None
    # Leader lock name
    # Only one active instance per leader lock can be active
    # at given moment
    # Config variables can be expanded as %(varname)s
    leader_lock_name = None
    # Pooled service are used to distribute load between services.
    # Pool name set in NOC_POOL parameter or --pool option.
    pooled = False
    # Format string to set process name
    # config variables can be expanded as %(name)s
    process_name = "noc-%(name).10s"
    # Connect to MongoDB on activate
    use_mongo = False
    # Initialize gettext and process *language* configuration
    use_translation = False
    # Initialize jinja2 templating engine
    use_jinja = False
    # Collect and send spans
    use_telemetry = False
    # Register traefik backend if not None
    traefik_backend = None
    # Traefik frontend rule
    # i.e. PathPrefix:/api/<name>
    traefik_frontend_rule = None
    # Require DCS health status to be considered healthy
    # Usually means resolution error to required services
    # temporary leads service to unhealthy state
    require_dcs_health = True
    # Use embedded router for messages
    use_router = False
    # Use service based consul check timeout
    dcs_check_interval: Optional[int] = None
    dcs_check_timeout: Optional[int] = None
    # Use watchdog for check Service register in consul
    use_watchdog = False

    LOG_FORMAT = config.log_format

    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    DEFAULT_SHARDING_KEY = "managed_object"
    SHARDING_KEYS = {"span": "ctx"}

    class RegistrationError(Exception):
        pass

    def __init__(self):
        set_service(self)
        sys.excepthook = excepthook
        self.loop: Optional[asyncio.BaseEventLoop] = None
        self.logger = logging.getLogger()
        self.service_id = str(uuid.uuid4())
        self.executors = {}
        self.start_time = perf_counter()
        self.pid = os.getpid()
        self.startup_ts = None
        self.telemetry_callback = None
        self.dcs = None
        # Message routed
        self.router: Optional[Router] = None
        # Effective address and port
        self.address = None
        self.port = None
        self.is_active = False
        # Can be initialized in subclasses
        self.scheduler = None
        # Liftbridge publisher
        self.publish_queue: Optional[MessageStreamQueue] = None
        self.publisher_start_lock = threading.Lock()
        # Metrics publisher buffer
        self.metrics_queue: Optional[QBuffer] = None
        # MX metrics publisher buffer
        self.mx_partitions: int = 0
        self.mx_queue: Optional[MBuffer] = None
        #
        self.active_subscribers = 0
        self.subscriber_shutdown_waiter: Optional[asyncio.Event] = None
        #
        self.watchdog_waiter: Optional[asyncio.Event] = None
        # Metrics partitions
        self.n_metrics_partitions = len(config.clickhouse.cluster_topology.split(","))
        #
        self.metrics_key_lock = threading.Lock()
        self.metrics_key_seq: int = 0

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Return argument parser
        """
        return argparse.ArgumentParser()

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Apply additional parser arguments
        """
        parser.add_argument(
            "--node", action="store", dest="node", default=config.node, help="NOC node name"
        )
        parser.add_argument(
            "--loglevel",
            action="store",
            choices=list(self.LOG_LEVELS),
            dest="loglevel",
            default=config.loglevel,
            help="Logging level",
        )
        parser.add_argument(
            "--instance",
            action="store",
            dest="instance",
            type=int,
            default=config.instance,
            help="Instance number",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="Dump additional debugging info",
        )
        parser.add_argument(
            "--dcs",
            action="store",
            dest="dcs",
            default=DEFAULT_DCS,
            help="Distributed Coordinated Storage URL",
        )
        if self.pooled:
            parser.add_argument(
                "--pool", action="store", dest="pool", default=config.pool, help="NOC pool name"
            )

    @classmethod
    def die(cls, msg: str = "") -> NoReturn:
        """
        Dump message to stdout and terminate process with error code
        """
        sys.stdout.write(str(msg) + "\n")
        sys.stdout.flush()
        os._exit(1)

    def setup_logging(self, loglevel=None):
        """
        Create new or setup existing logger
        """
        # @todo: Duplicates config.setup_logging
        if not loglevel:
            loglevel = config.loglevel
        logger = logging.getLogger()
        if len(logger.handlers):
            # Logger is already initialized
            fmt = ErrorFormatter(self.LOG_FORMAT, None)
            for h in logging.root.handlers:
                if isinstance(h, logging.StreamHandler):
                    h.stream = sys.stdout
                h.setFormatter(fmt)
            logging.root.setLevel(loglevel)
        else:
            # Initialize logger
            logging.basicConfig(stream=sys.stdout, format=self.LOG_FORMAT, level=loglevel)
        self.logger = logging.getLogger(self.name)
        logging.captureWarnings(True)

    def setup_test_logging(self):
        self.logger = logging.getLogger(self.name)

    def setup_translation(self):
        from noc.core.translation import set_translation, ugettext

        set_translation(self.name, config.language)
        if self.use_jinja:
            from jinja2.defaults import DEFAULT_NAMESPACE

            if "_" not in DEFAULT_NAMESPACE:
                DEFAULT_NAMESPACE["_"] = ugettext

    def on_change_loglevel(self, old_value, new_value):
        if new_value not in self.LOG_LEVELS:
            self.logger.error("Invalid loglevel '%s'. Ignoring", new_value)
            return
        self.logger.warning("Changing loglevel to %s", new_value)
        logging.getLogger().setLevel(self.LOG_LEVELS[new_value])

    def log_separator(self, symbol="*", length=72):
        """
        Log a separator string to visually split log
        """
        self.logger.warning(symbol * length)
        if config.features.forensic:
            self.logger.warning("[noc.core.forensic] [=Process restarted]")

    def setup_signal_handlers(self):
        """
        Set up signal handlers
        """
        signal.signal(signal.SIGTERM, self.on_SIGTERM)
        if os.name == "nt":
            # Ctrl+C. For cancel traced Ctrl + Break
            signal.signal(signal.SIGINT, self.on_SIGTERM)
        else:
            signal.signal(signal.SIGHUP, self.on_SIGHUP)

    def set_proc_title(self):
        """
        Set process title
        """
        v = {"name": self.name, "instance": config.instance or "", "pool": config.pool or ""}
        title = self.process_name % v
        self.logger.debug("Setting process title to: %s", title)
        setproctitle.setproctitle(title)

    def start(self):
        """
        Run main server loop
        """
        self.startup_ts = perf_counter()
        parser = self.create_parser()
        self.add_arguments(parser)
        options = parser.parse_args(sys.argv[1:])
        cmd_options = vars(options)
        cmd_options.pop("args", ())
        # Bootstrap logging with --loglevel
        self.setup_logging(cmd_options["loglevel"])
        self.log_separator()
        # Setup timezone
        try:
            self.logger.info("Setting timezone to %s", config.timezone)
            setup_timezone()
        except ValueError as e:
            self.die(str(e))
        # Setup title
        self.set_proc_title()
        # Setup signal handlers
        self.setup_signal_handlers()
        self.on_start()
        # Starting IOLoop
        self.is_active = True
        if self.pooled:
            self.logger.warning("Running service %s (pool: %s)", self.name, config.pool)
        else:
            self.logger.warning("Running service %s", self.name)
        try:
            setup_asyncio()
            self.loop = asyncio.get_event_loop()
            # Initialize DCS
            self.dcs = get_dcs(cmd_options["dcs"])
            # Activate service
            self.loop.create_task(self.activate())
            self.logger.warning("Starting IOLoop")
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.logger.warning("Interrupted by Ctrl+C")
        except self.RegistrationError:
            self.logger.info("Registration failed")
        except Exception:
            error_report()
        finally:
            if self.loop:
                self.loop.create_task(self.deactivate())
        self.logger.warning("Service %s has been terminated", self.name)

    def get_event_loop(self) -> asyncio.BaseEventLoop:
        return self.loop

    def on_start(self):
        """
        Reload config
        """
        if self.use_translation:
            self.setup_translation()

    def stop(self):
        self.logger.warning("Stopping")
        self.loop.create_task(self.deactivate())

    def on_SIGHUP(self, signo, frame):
        # self.logger.warning("SIGHUP caught, rereading config")
        pass

    def on_SIGTERM(self, signo, frame):
        self.logger.warning("SIGTERM caught, Stopping")
        self.stop()

    def get_service_address(self) -> Tuple[str, int]:
        """
        Returns an (address, port) for HTTP service listener
        """
        if self.address and self.port:
            return self.address, self.port
        if config.listen:
            addr, port = config.listen.split(":")
            port_tracker = config.instance
        else:
            addr, port = "auto", 0
            port_tracker = 0
        if addr == "auto":
            addr = config.node
            self.logger.info("Autodetecting address: auto -> %s", addr)
        addr = config.node
        port = int(port) + port_tracker
        return addr, port

    async def init_api(self):
        """
        Initialize API routers and handlers
        :return:
        """
        raise NotImplementedError

    async def shutdown_api(self):
        """
        Stop API services
        :return:
        """
        raise NotImplementedError

    async def activate(self):
        """
        Initialize services before run
        """
        self.logger.warning("Activating service")
        if self.use_mongo:
            from noc.core.mongo.connection import connect

            connect()

        await self.init_api()
        #
        if config.message.embedded_router and self.use_router:
            self.router = Router()
            self.router.load()
            asyncio.get_running_loop().create_task(self.get_mx_routes_config())
        if not config.message.embedded_router and config.message.enable_metrics:
            self.mx_partitions = await self.get_stream_partitions("message")
        #
        if self.use_telemetry or self.use_router:
            self.start_telemetry_callback()
        self.loop.create_task(self.on_register())

    async def deactivate(self):
        if not self.is_active:
            self.logger.info("Not Active")
            return
        self.is_active = False
        self.logger.info("Deactivating")
        # Shutdown API
        await self.shutdown_api()
        # Shutdown subscriptions
        await self.shutdown_subscriptions()
        # Release registration
        if self.dcs:
            self.logger.info("Deregistration")
            await self.dcs.deregister()
        # Shutdown schedulers
        if self.scheduler:
            try:
                self.logger.info("Shutting down scheduler")
                await self.scheduler.shutdown()
            except asyncio.TimeoutError:
                self.logger.info("Timed out when shutting down scheduler")
        # Shutdown executors
        await self.shutdown_executors()
        # Custom deactivation
        await self.on_deactivate()
        # Shutdown Liftbridge publisher
        await self.shutdown_publisher()
        # Continue deactivation
        # Finally stop ioloop
        self.dcs = None
        self.logger.info("Stopping EventLoop")
        self.loop.stop()
        m = {}
        apply_metrics(m)
        apply_hists(m)
        apply_quantiles(m)
        self.logger.info("Post-mortem metrics: %s", m)
        self.die("")

    def get_register_tags(self):
        tags = ["noc"]
        if config.features.traefik:
            if self.traefik_backend and self.traefik_frontend_rule:
                tags += [
                    "traefik.tags=backend",
                    "traefik.backend=%s" % self.traefik_backend,
                    "traefik.frontend.rule=%s" % self.traefik_frontend_rule,
                    "traefik.backend.load-balancing=wrr",
                ]
                weight = self.get_backend_weight()
                if weight:
                    tags += ["traefik.backend.weight=%s" % weight]
                limit = self.get_backend_limit()
                if limit:
                    tags += ["traefik.backend.maxconn.amount=%s" % limit]
        return tags

    async def on_register(self):
        addr, port = self.get_service_address()
        r = await self.dcs.register(
            self.name,
            addr,
            port,
            pool=config.pool if self.pooled else None,
            lock=self.get_leader_lock_name(),
            tags=self.get_register_tags(),
            check_interval=self.dcs_check_interval,
            check_timeout=self.dcs_check_timeout,
        )
        if r:
            # Finally call on_activate
            await self.on_activate()
            self.logger.info("Service is active (in %.2fms)", self.uptime() * 1000)
            if self.use_watchdog and not hasattr(self, "slot_number") and not self.leader_lock_name:
                # Run Watchdog, ignore service with slot
                self.logger.info("Start Watchdog")
                self.watchdog_waiter = asyncio.Event()
                self.loop.create_task(self.watchdog())
        else:
            raise self.RegistrationError()

    async def on_activate(self):
        """
        Called when service activated
        """
        return

    async def acquire_lock(self):
        await self.dcs.acquire_lock("lock-%s" % self.name)

    async def acquire_slot(self):
        if self.pooled:
            name = "%s-%s" % (self.name, config.pool)
        else:
            name = self.name
        slot_number, total_slots = await self.dcs.acquire_slot(name, config.global_n_instances)
        if total_slots <= 0:
            self.die("Service misconfiguration detected: Invalid total_slots")
        return slot_number, total_slots

    async def on_deactivate(self):
        return

    def open_rpc(self, name, pool=None, sync=False, hints=None):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc, sync=sync, hints=hints)

    def get_mon_status(self):
        return True

    def get_mon_data(self):
        """
        Returns monitoring data
        """
        r = {
            "status": self.get_mon_status(),
            "service": self.name,
            "instance": str(self.service_id),
            "node": config.node,
            "pid": self.pid,
            # Current process uptime
            "uptime": perf_counter() - self.start_time,
        }
        if self.pooled:
            r["pool"] = config.pool
        if self.executors:
            for x in self.executors:
                self.executors[x].apply_metrics(r)
        apply_metrics(r)
        if self.publish_queue:
            self.publish_queue.apply_metrics(r)
        apply_hists(r)
        apply_quantiles(r)
        return r

    def iter_rpc_retry_timeout(self) -> Iterable[float]:
        """
        Yield timeout to wait after unsuccessful RPC connection
        """
        for t in config.rpc.retry_timeout.split(","):
            yield float(t)

    async def subscribe_stream(
        self,
        stream: str,
        partition: int,
        handler: Callable[
            [Message],
            Awaitable[None],
        ],
        start_timestamp: Optional[float] = None,
        cursor_id: Optional[str] = None,
        auto_set_cursor: bool = True,
        async_cursor: bool = False,
        async_cursor_condition: asyncio.Condition = None,
    ) -> None:
        # @todo: Restart on failure
        async def set_cursor_sync(offset: int) -> None:
            """
            Synchronous version of cursor setter.
            Blocks until the cursor is really set.
            :param offset:
            :return:
            """
            await client.set_cursor(
                stream=stream,
                partition=partition,
                cursor_id=cursor_id,
                offset=offset,
            )

        async def set_cursor_async(offset: int) -> None:
            """
            Asynchronous version of cursor setter. Doesn't block subscriber loop,
            though committed cursor position may lag behind the really processed one.
            :param offset:
            :return:
            """
            nonlocal cursor_cond, cursor_offset
            async with cursor_cond:
                cursor_offset = offset
                if not async_cursor_condition:
                    cursor_cond.notify_all()

        async def cursor_setter() -> None:
            nonlocal cursor_cond, cursor_offset
            offset: int = -1
            while True:
                # Wait for change
                async with cursor_cond:
                    await cursor_cond.wait()
                    changed = cursor_offset > offset
                    offset = cursor_offset
                # Set cursor
                if changed:
                    await set_cursor_sync(offset)
                if self.subscriber_shutdown_waiter:
                    break

        self.logger.info("Subscribing %s:%s", stream, partition)
        cursor_id = cursor_id or self.name
        # Setup cursor setter
        if auto_set_cursor and cursor_id:
            if async_cursor or async_cursor_condition:
                set_cursor = set_cursor_async
                cursor_cond = async_cursor_condition or asyncio.Condition()
                cursor_offset: int = -1
                asyncio.get_running_loop().create_task(cursor_setter())
            else:
                set_cursor = set_cursor_sync
        else:
            set_cursor = None
        # Main subscriber loop
        try:
            async with MessageStreamClient() as client:
                self.active_subscribers += 1
                async for msg in client.subscribe(
                    stream=stream,
                    partition=partition,
                    cursor_id=self.name,
                    start_timestamp=start_timestamp,
                ):
                    span_id = msg.headers.get(MX_SPAN_ID)
                    span_ctx = msg.headers.get(MX_SPAN_CTX)
                    sample = 1 if span_ctx and span_id else 0
                    with Span(
                        server=self.name,
                        service="on_message",
                        sample=sample,
                        parent=span_id,
                        context=span_ctx,
                        in_label=msg.offset,
                        headers=msg.headers,
                    ) as span:
                        try:
                            await handler(msg)
                        except Exception as e:
                            self.logger.error(
                                "Failed to process message offset %s: %s", msg.offset, e
                            )
                            error_report(logger=self.logger)
                            span.error_text = str(e)
                    if set_cursor:
                        await set_cursor(msg.offset)
                    if self.subscriber_shutdown_waiter:
                        break
        finally:
            self.active_subscribers -= 1
        if self.subscriber_shutdown_waiter and not self.active_subscribers:
            self.subscriber_shutdown_waiter.set()

    def _init_publisher(self):
        """
        Spin-up publisher and queue
        :return:
        """
        with self.publisher_start_lock:
            if self.publish_queue:
                return  # Created in concurrent thread
            self.publish_queue = MessageStreamQueue(self.loop)
            self.metrics_queue = QBuffer(max_size=int(config.msgstream.max_message_size * 99 / 100))
            self.mx_queue = MBuffer()
            self.loop.create_task(self.publisher())
            self.loop.create_task(self.publish_metrics(self.metrics_queue))
            self.loop.create_task(self.message_route())

    def publish(
        self,
        value: bytes,
        stream: str,
        partition: Optional[int] = None,
        key: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ):
        """
        Schedule publish request
        :param value:
        :param stream:
        :param partition:
        :param key:
        :param headers:
        :return:
        """
        if not self.publish_queue:
            self._init_publisher()
        req = MessageStreamClient.get_publish_request(
            data=value, stream=stream, partition=partition, sharding_key=key, headers=headers
        )
        self.publish_queue.put(req)

    async def publisher(self):
        async with MessageStreamClient() as client:
            while not self.publish_queue.to_shutdown:
                req = await self.publish_queue.get(timeout=1)
                if not req:
                    continue  # Timeout or shutdown
                try:
                    await client.publish_request(req, wait_for_stream=True)
                except MsgStreamError as e:
                    self.logger.error("Failed to publish message: %s", e)
                    self.logger.error("Retry message")
                    await asyncio.sleep(1)
                    self.publish_queue.put(req, fifo=False)

    async def shutdown_executors(self):
        if self.executors:
            self.logger.info("Shutting down executors")
            for x in self.executors:
                try:
                    self.logger.info("Shutting down %s", x)
                    await self.executors[x].shutdown()
                except asyncio.TimeoutError:
                    self.logger.info("Timed out when shutting down %s", x)

    async def shutdown_subscriptions(self):
        self.logger.info("Shutting down subscriptions")
        self.subscriber_shutdown_waiter = asyncio.Event()
        try:
            await asyncio.wait_for(self.subscriber_shutdown_waiter.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.info(
                "Timed out when shutting down subscriptions. Some message may be still processing"
            )

    async def shutdown_publisher(self):
        if self.publish_queue:
            r = await self.publish_queue.drain(5.0)
            if not r:
                self.logger.info(
                    "Unclean shutdown of liftbridge queue. Up to %d messages may be lost",
                    self.publish_queue.qsize(),
                )
            self.publish_queue.shutdown()

    def get_executor(self, name: str) -> ThreadPoolExecutor:
        """
        Return or start named executor
        """
        executor = self.executors.get(name)
        if not executor:
            xt = "%s.%s_threads" % (self.name, name)
            max_threads = config.get_parameter(xt)
            self.logger.info(
                "Starting threadpool executor %s (up to %d threads)", name, max_threads
            )
            executor = ThreadPoolExecutor(max_threads, name=name)
            self.executors[name] = executor
        return executor

    def run_in_executor(
        self, name: str, fn: Callable[[Any], T], *args: Any, **kwargs: Any
    ) -> asyncio.Future:
        executor = self.get_executor(name)
        return executor.submit(fn, *args, **kwargs)

    async def message_route(self):
        """
        Route messages from mx_queue
        :return:
        """
        self.logger.info("Starting Message Routing")
        while not (self.publish_queue.to_shutdown and self.mx_queue.is_empty()):
            t0 = perf_counter()
            for msg in self.mx_queue.iter_slice():
                # self.publish(chunk, stream=stream, partition=partition, headers=headers)
                await self.router.route_message(msg)
            if not self.publish_queue.to_shutdown:
                to_sleep = config.msgstream.metrics_send_delay - (perf_counter() - t0)
                if to_sleep > 0:
                    await asyncio.sleep(to_sleep)

    async def publish_metrics(
        self, queue: QBuffer, headers: Optional[Dict[str, bytes]] = None
    ) -> None:
        """
        Schedule metrics to send stream

        :param queue: Metrics Queue
        :param headers: Message Headers
        """
        while not (self.publish_queue.to_shutdown and queue.is_empty()):
            t0 = perf_counter()
            for stream, partition, chunk in queue.iter_slice():
                self.publish(chunk, stream=stream, partition=partition, headers=headers)
            if not self.publish_queue.to_shutdown:
                to_sleep = config.msgstream.metrics_send_delay - (perf_counter() - t0)
                if to_sleep > 0:
                    await asyncio.sleep(to_sleep)

    def register_metrics(
        self, table: str, metrics: List[Dict[str, Any]], key: Optional[int] = None
    ):
        """
        Schedule metrics to be sent to the `table`.

        :param table: Table name
        :param metrics: List of dicts containing metrics records
        :param key: Sharding key, None for round-robin distribution
        :return:
        """
        if key is None:
            with self.metrics_key_lock:
                key = self.metrics_key_seq
                self.metrics_key_seq += 1
        if not self.publish_queue:
            self._init_publisher()
        self.metrics_queue.put(
            stream=f"ch.{table}", partition=key % self.n_metrics_partitions, data=metrics
        )

    def start_telemetry_callback(self) -> None:
        """
        Run telemetry callback
        :return:
        """
        self.telemetry_callback = PeriodicCallback(self.send_telemetry, 250)
        self.telemetry_callback.start()

    async def send_telemetry(self):
        """
        Publish telemetry data

        :return:
        """
        spans = get_spans()
        if spans:
            self.register_metrics("span", [span_to_dict(s) for s in spans])

    async def get_mx_routes_config(self):
        """
        Subscribe and track datastream changes
        """
        client = RouteDataStreamClient("cfgmxroute", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track MX route settings")
            try:
                await client.query(limit=config.message.ds_limit, block=True)
            except NOCError as e:
                self.logger.info("Failed to get MX route settings: %s", e)
                await asyncio.sleep(1)

    async def update_route(self, data: Dict[str, Any]) -> None:
        self.router.change_route(data)

    async def delete_route(self, r_id: str) -> None:
        self.router.delete_route(r_id)

    async def send_message(
        self,
        data: Any,
        message_type: str,
        headers: Optional[Dict[str, bytes]] = None,
        sharding_key: int = 0,
        store: bool = False,
    ):
        """
        Build message and schedule to send to mx service

        :param data: Data for transmit
        :param message_type: Message type
        :param headers: additional message headers
        :param sharding_key: Key for sharding over MX services
        :param store: Append message to buffer for deliver
        :return:
        """
        msg = Router.get_message(data, message_type, headers, sharding_key)
        self.logger.debug("Send message: %s", msg)
        if not config.message.embedded_router:
            self.publish(
                value=msg.value,
                stream=MX_STREAM,
                partition=sharding_key % self.mx_partitions,
                headers=msg.headers,
            )
            return
        if store:
            self.mx_queue.put(msg)
        else:
            await self.router.route_message(msg)

    def register_message(
        self,
        data: Any,
        message_type: str,
        headers: Optional[Dict[str, bytes]] = None,
        sharding_key: int = 0,
        group_key: Optional[str] = None,
    ):
        """
        Register message for deliver
        :param data: Data for transmit
        :param message_type: Message type
        :param headers: additional message headers
        :param sharding_key: Key for sharding over MX services
        :param group_key:
        :return:
        """
        msg = Router.get_message(
            data,
            message_type,
            headers,
            sharding_key,
            raw_value=bool(group_key),
        )
        self.mx_queue.put(msg, group_key)

    def get_leader_lock_name(self):
        if self.leader_lock_name:
            return self.leader_lock_name % {"pool": config.pool}
        return None

    def get_backend_weight(self):
        """
        Return backend weight for weighted load balancers
        (i.e. traefik).
        Return None for default weight
        :return:
        """
        return None

    def get_backend_limit(self):
        """
        Return backend connection limit for load balancers
        (i.e. traefik)
        Return None for no limits
        :return:
        """
        return None

    def is_valid_health_check(self, service_id):
        """
        Check received service id matches own service id
        :param service_id:
        :return:
        """
        return not (
            self.dcs
            and self.dcs.health_check_service_id
            and self.dcs.health_check_service_id != service_id
        )

    def get_health_status(self):
        """
        Check service health to be reported to service registry
        :return: (http code, message)
        """
        if self.dcs and self.require_dcs_health:
            # DCS is initialized
            return self.dcs.get_status()
        return 200, "OK"

    def uptime(self):
        if not self.startup_ts:
            return 0
        return perf_counter() - self.startup_ts

    async def get_stream_partitions(self, stream: str) -> int:
        """

        :param stream:
        :return:
        """
        async with MessageStreamClient() as client:
            while True:
                meta = await client.fetch_metadata()
                if meta.metadata:
                    if stream in meta.metadata:
                        if meta.metadata[stream]:
                            return len(meta.metadata[stream])
                        break
                # Cluster election in progress or cluster is misconfigured
                self.logger.info("Stream '%s' has no active partitions. Waiting" % stream)
                await asyncio.sleep(1)

    @staticmethod
    @cachetools.cached(cachetools.TTLCache(maxsize=128, ttl=60))
    def get_slot_limits(slot_name):
        """
        Get slot count
        :param slot_name:
        :return:
        """
        from noc.core.dcs.loader import get_dcs
        from noc.core.ioloop.util import run_sync

        dcs = get_dcs()
        return run_sync(partial(dcs.get_slot_limit, slot_name))

    async def on_route_rules_ready(self) -> None:
        """
        Called when all Router rules are ready.
        """
        return

    async def watchdog(self):
        """
        WatchDog task. View watchdog_waiter event, by setting /health API.
        If not set event - force reboot process
        :return:
        """
        failed, delay, deviation = 0, config.watchdog.check_interval, 0.5
        while True:
            await asyncio.sleep(delay - deviation + 2 * deviation * random.random())
            self.logger.info("WatchDog loop")
            if not self.watchdog_waiter.is_set() and failed > config.watchdog.failed_count:
                self.logger.warning("WatchDog is more %s failed. Deactivate process", failed)
                self.stop()
            elif not self.watchdog_waiter.is_set():
                failed += 1
                continue
            self.watchdog_waiter.clear()
            failed = 0