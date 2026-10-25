# ----------------------------------------------------------------------
# Base service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
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
    Any,
    Never,
)
from collections.abc import Callable, Awaitable, Coroutine, Iterable
import socket

# Third-party modules
import setproctitle
from granian.constants import Interfaces
from granian.net import SocketSpec
from granian.server.embed import Server
from granian.utils.proxies import wrap_asgi_with_proxy_headers
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.encoders import jsonable_encoder
from a2wsgi import WSGIMiddleware

# NOC modules
from noc.config import config
from noc.core.affinity import AffinityController, AFF_NONE
from noc.core.debug import excepthook, error_report
from noc.core.perf import apply_metrics
from noc.core.hist.monitor import apply_hists
from noc.core.quantile.monitor import apply_quantiles
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from noc.core.threadpool import ThreadPoolExecutor
from noc.core.span import get_spans, span_to_dict
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
from noc.core.mx import MX_STREAM, MX_SPAN_CTX, MX_SPAN_ID, MessageType
from noc.core.span import Span
from noc.core.validators import is_ipv4
from noc.core.version import version
from noc.core.log import PrefixLoggerAdapter
from .rpc import RPCProxy
from .loader import set_service
from .paths.loader import loader, ServicePathLoader
from .middleware.logging import LoggingMiddleware
from .middleware.span import SpanMiddleware
from ..router.datastream import RouteDataStreamClient

DCS_SLOTS_CACHE = {}  # PROCESS -> object cache
dcs_slot_lock = threading.Lock()


class NOCGranianServer(Server):
    """Embedded Granian server that shares one bound listener with its worker."""

    def _init_shared_socket(self) -> None:
        self._ssp = SocketSpec(self.bind_addr, self.bind_port, self.backlog)
        self._shd = self._ssp.build()
        self._sfd = self._shd.get_fd()
        self._ssp = None


class BaseService:
    """Basic service implementation."""

    BASE_OPENAPI_TAGS_DOCS = {
        "internal": "NOC internal API, including healthchecks, monitoring and tooling",
        "JSON-RPC API": "Implemented by JSON-RPC specification 1.0",
    }
    # Additional OpenAPI tags docs, tag -> description
    OPENAPI_TAGS_DOCS: dict[str, str] = {}

    # Service name
    name: str
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
    # Require DCS health status to be considered healthy
    # Usually means resolution error to required services
    # temporary leads service to unhealthy state
    require_dcs_health = True
    # Use embedded router for messages
    use_router = False
    # Use service based consul check timeout
    dcs_check_interval: int | None = None
    dcs_check_timeout: int | None = None
    # Use watchdog for check Service register in consul
    use_watchdog = False

    LOG_FORMAT = config.log_format

    DEFAULT_SHARDING_KEY = "managed_object"
    SHARDING_KEYS = {"span": "ctx"}

    class RegistrationError(Exception):
        pass

    def __init__(self) -> None:
        set_service(self)
        sys.excepthook = excepthook
        self.loop: asyncio.BaseEventLoop | None = None
        self.background_tasks: set[asyncio.Task[Any]] = set()
        self.logger = logging.getLogger()
        self.service_id = str(uuid.uuid4())
        self.executors = {}
        self.start_time = perf_counter()
        self.pid = os.getpid()
        self.startup_ts = None
        self.telemetry_callback = None
        self.dcs = None
        # Message routed
        self.router: Router | None = None
        # Effective address and port
        self.address = None
        self.port = None
        self.app: FastAPI | None = None
        # WSGI application of any third-party framework attached to the main API.
        self.wsgi_app = None
        # Collect 'api_requests' metric for API calls
        self.collect_req_api_metric = False
        self.server: NOCGranianServer | None = None
        self.server_task: asyncio.Task | None = None
        self.is_active = False
        # Can be initialized in subclasses
        self.scheduler = None
        # Liftbridge publisher
        self.publish_queue: MessageStreamQueue | None = None
        self.publisher_start_lock = threading.Lock()
        # Metrics publisher buffer
        self.metrics_queue: QBuffer | None = None
        # MX metrics publisher buffer
        self.mx_partitions: int = 0
        self.mx_queue: MBuffer | None = None
        self.active_subscribers = 0
        self.subscriber_shutdown_waiter: asyncio.Event | None = None
        self.watchdog_waiter: asyncio.Event | None = None
        # Metrics partitions
        self.n_metrics_partitions = len(config.clickhouse.cluster_topology.split(","))
        self.metrics_key_lock = threading.Lock()
        self.metrics_key_seq: int = 0

    def create_parser(self) -> argparse.ArgumentParser:
        """Return argument parser"""
        return argparse.ArgumentParser()

    def start_background_task[T](
        self, coro: Coroutine[Any, Any, T], *, name: str | None = None
    ) -> asyncio.Task[T]:
        """Create a task and retain its reference until it completes."""
        task = asyncio.create_task(coro, name=name)
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        return task

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Apply additional parser arguments"""
        parser.add_argument(
            "--node", action="store", dest="node", default=config.node, help="NOC node name"
        )
        parser.add_argument(
            "--loglevel",
            action="store",
            choices=["critical", "error", "warning", "info", "debug"],
            dest="loglevel",
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
    def die(cls, msg: str = "") -> Never:
        """Dump message to stdout and terminate process with error code"""
        sys.stdout.write(str(msg) + "\n")
        sys.stdout.flush()
        os._exit(1)

    def setup_test_logging(self) -> None:
        self.logger = logging.getLogger(self.name)

    def setup_translation(self) -> None:
        from noc.core.translation import set_translation, ugettext

        set_translation(self.name, config.language)
        if self.use_jinja:
            from jinja2.defaults import DEFAULT_NAMESPACE

            if "_" not in DEFAULT_NAMESPACE:
                DEFAULT_NAMESPACE["_"] = ugettext

    def log_separator(self, symbol: str = "*", length: int = 72) -> None:
        """Log a separator string to visually split log"""
        self.logger.warning(symbol * length)
        if config.features.forensic:
            self.logger.warning("[noc.core.forensic] [=Process restarted]")

    def setup_signal_handlers(self) -> None:
        """Set up signal handlers"""
        signal.signal(signal.SIGTERM, self.on_SIGTERM)
        if os.name == "nt":
            # Ctrl+C. For cancel traced Ctrl + Break
            signal.signal(signal.SIGINT, self.on_SIGTERM)
        else:
            signal.signal(signal.SIGHUP, self.on_SIGHUP)

    def set_proc_title(self) -> None:
        """Set process title"""
        v = {"name": self.name, "instance": config.instance or "", "pool": config.pool or ""}
        title = self.process_name % v
        self.logger.debug("Setting process title to: %s", title)
        setproctitle.setproctitle(title)

    def set_cpu_affinity(self) -> None:
        """Apply CPU affinity settings."""
        expected = AffinityController.effective_affinity(config.process.cpu_affinity)
        if expected is AFF_NONE:
            return
        if not AffinityController.supports_set:
            self.logger.info(
                "CPU affinity is configured, but setting CPU affinity is not supported. Skipping"
            )
            return
        self.logger.info("Setting CPU affinity to %s", ", ".join(str(x) for x in sorted(expected)))
        AffinityController.set_affinity(expected)

    def start(self) -> None:
        """Run main server loop"""
        self.startup_ts = perf_counter()
        parser = self.create_parser()
        self.add_arguments(parser)
        options = parser.parse_args(sys.argv[1:])
        cmd_options = vars(options)
        cmd_options.pop("args", ())
        # Bootstrap logging with --loglevel
        # Apply --loglevel when necessary
        loglevel = cmd_options.get("loglevel")
        if loglevel:
            config.loglevel = loglevel
        # Apply configuration setup
        config.setup()
        self.log_separator()
        # Setup title
        self.set_proc_title()
        # Setup signal handlers
        self.setup_signal_handlers()
        # Setup CPU affinity
        self.set_cpu_affinity()
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

    def on_start(self) -> None:
        """Reload config"""
        if self.use_translation:
            self.setup_translation()

    def stop(self) -> None:
        self.logger.warning("Stopping")
        self.loop.create_task(self.deactivate())

    def on_SIGHUP(self, signo, frame) -> None:
        # self.logger.warning("SIGHUP caught, rereading config")
        pass

    def on_SIGTERM(self, signo, frame) -> None:
        self.logger.warning("SIGTERM caught, Stopping")
        self.stop()

    def get_service_address(self) -> tuple[str, int]:
        """Returns an (address, port) for HTTP service listener"""
        if self.address and self.port:
            return self.address, self.port  # Already resolved
        if config.listen:
            addr, port = config.listen.split(":")
            port_tracker = config.instance
        else:
            addr, port = "auto", 0
            port_tracker = 0
        if addr == "auto":
            addr = config.node
            self.logger.info("Autodetecting address to %s", addr)
        elif not is_ipv4(addr):
            addr = self.resolve_addr(addr)
            self.logger.info("Resolving address to %s", addr)
        port = int(port) + port_tracker
        return addr, port

    def resolve_addr(self, addr: str) -> str:
        """Resolve symbolic name to address.

        Tries to:

        1. Resolve to interface name.
        2. Or leave untouched.

        Args:
            addr: Symbolic name.

        Returns:
            Resolved address.
        """
        import psutil

        if_addrs = psutil.net_if_addrs()
        if if_addrs.get(addr):
            r = [a.address for a in if_addrs[addr] if a.family == socket.AddressFamily.AF_INET]
            if r:
                return r[0]
        return addr  # Leave untouched

    async def error_handler(self, request: Request, exc: Exception) -> Response:
        """Handle unhandled API exceptions."""
        error_report(logger=self.logger)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "error_description": f"Internal Server Error: {exc}",
                "error_uri": str(request.url),
            },
        )

    async def http_error_handler(self, request: Request, exc: HTTPException) -> Response:
        """Handle HTTP errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "invalid_request",
                "error_description": f"{exc.detail}",
                "error_uri": str(request.url),
            },
        )

    async def request_validation_error_handler(
        self, request: Request, exc: RequestValidationError
    ) -> Response:
        """Handle request validation and customize the response."""
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_request",
                "error_description": jsonable_encoder(exc.errors()),
                "error_uri": str(request.url),
            },
        )

    def get_granian_options(self) -> dict[str, Any]:
        """Return service-specific Granian server options."""
        return {}

    def configure_api_routes(self, app: FastAPI) -> None:
        """Configure service-specific API routes."""

    async def init_api(self) -> None:
        """Initialize the FastAPI application, routers, middleware, and server."""
        # Build tags docs
        openapi_tags = [
            {"name": tag, "description": self.BASE_OPENAPI_TAGS_DOCS[tag]}
            for tag in self.BASE_OPENAPI_TAGS_DOCS
        ]
        if self.OPENAPI_TAGS_DOCS:
            openapi_tags.extend(
                {"name": tag, "description": self.OPENAPI_TAGS_DOCS[tag]}
                for tag in self.OPENAPI_TAGS_DOCS
            )
        app = FastAPI(
            title=f"NOC '{self.name or 'unknown'}' Service API",
            version=version.version,
            openapi_url=f"/api/{self.name}/openapi.json",
            docs_url=f"/api/{self.name}/docs",
            redoc_url=f"/api/{self.name}/redoc",
            openapi_tags=openapi_tags,
            exception_handlers={
                Exception: self.error_handler,
                HTTPException: self.http_error_handler,
                RequestValidationError: self.request_validation_error_handler,
            },
        )
        self.app = app
        app.add_middleware(
            LoggingMiddleware,
            logger=PrefixLoggerAdapter(self.logger, "api"),
            is_wsgi_app=bool(self.wsgi_app),
            collect_req_api_metric=self.collect_req_api_metric,
        )
        app.add_middleware(SpanMiddleware, service_name=self.name)
        # Initialize routers
        for path in loader.iter_classes():
            app.include_router(loader.get_class(path))
        service_paths = ("services", self.name, "paths")
        if os.path.exists(os.path.join(*service_paths)):
            extra_loader = ServicePathLoader()
            extra_loader.base_path = service_paths
            for path in extra_loader.iter_classes():
                kls = extra_loader.get_class(path)
                if kls:
                    app.include_router(kls)
        self.configure_api_routes(app)
        # Attach third-party WSGI application
        if self.wsgi_app:
            app.mount("/", WSGIMiddleware(self.wsgi_app))
        addr, port = self.get_service_address()
        # Apply proxy headers with Granian's ASGI wrapper.
        asgi_app = wrap_asgi_with_proxy_headers(app, trusted_hosts="*")
        startup_complete = asyncio.Event()

        async def app_with_startup_signal(scope, receive, send):
            async def send_with_startup_signal(message):
                await send(message)
                if message["type"] == "lifespan.startup.complete":
                    startup_complete.set()

            await asgi_app(scope, receive, send_with_startup_signal)

        server = NOCGranianServer(
            app_with_startup_signal,
            address=addr,
            port=port,
            interface=Interfaces.ASGI,
            backlog=2048,
            log_access=True,
            log_access_format="%(method)s %(path)s %(status)d",
            log_enabled=True,
            **self.get_granian_options(),
        )
        self.server = server
        assert self.loop is not None
        server_task = self.loop.create_task(server.serve())
        self.server_task = server_task
        startup_task = self.loop.create_task(startup_complete.wait())
        done, _ = await asyncio.wait(
            (startup_task, server_task), return_when=asyncio.FIRST_COMPLETED
        )
        if server_task in done and not startup_complete.is_set():
            startup_task.cancel()
            try:
                await startup_task
            except asyncio.CancelledError:
                pass
            await server_task
            raise RuntimeError("Granian stopped before API startup completed")
        await startup_task
        if server_task.done():
            await server_task
        self.address, self.port = self.get_effective_address()
        self.logger.info("Running HTTP APIs at http://%s:%s/", self.address, self.port)
        self.logger.info(
            "Running HTTP APIs Docs at http://%s:%s/api/%s/docs", self.address, self.port, self.name
        )

    async def shutdown_api(self) -> None:
        """Stop the API server."""
        self.logger.info("Shutdown FAST API")
        assert self.server is not None
        self.server.stop()
        assert self.server_task is not None
        await self.server_task

    def get_effective_address(self) -> tuple[str, int]:
        assert self.server is not None
        socket_holder = self.server._shd
        if socket_holder is None:
            raise RuntimeError("No listening socket found")
        family = socket.AF_INET6 if ":" in self.server.bind_addr else socket.AF_INET
        with socket.fromfd(socket_holder.get_fd(), family, socket.SOCK_STREAM) as listener:
            address, port = listener.getsockname()[:2]
            return address, port

    async def activate(self) -> None:
        """Initialize services before run"""
        self.logger.warning("Activating service")
        if self.use_mongo:
            from noc.core.mongo.connection import connect

            connect()

        await self.init_api()
        if config.message.embedded_router and self.use_router:
            self.router = Router()
            self.router.load()
            self.start_background_task(self.get_mx_routes_config())
        if not config.message.embedded_router and config.message.enable_metrics:
            self.mx_partitions = await self.get_stream_partitions("message")
        if self.use_telemetry or self.use_router:
            self.start_telemetry_callback()
        self.loop.create_task(self.on_register())

    async def deactivate(self) -> None:
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
            except TimeoutError:
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

    def get_register_tags(self) -> list[str]:
        return ["noc"]

    async def on_register(self) -> None:
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

    async def on_activate(self) -> None:
        """Called when service activated"""

    async def acquire_lock(self) -> None:
        await self.dcs.acquire_lock(f"lock-{self.name}")

    async def acquire_slot(self) -> None:
        if self.pooled:
            name = f"{self.name}-{config.pool}"
        else:
            name = self.name
        slot_number, total_slots = await self.dcs.acquire_slot(name, config.global_n_instances)
        if total_slots <= 0:
            self.die("Service misconfiguration detected: Invalid total_slots")
        return slot_number, total_slots

    async def on_deactivate(self) -> None:
        return None

    def open_rpc(self, name: str, pool: str | None = None, sync: bool = False, hints=None):
        """Returns RPC proxy object."""
        return RPCProxy(self, f"{name}-{pool}" if pool else name, sync=sync, hints=hints)

    def get_mon_status(self) -> bool:
        return True

    def get_mon_data(self) -> dict[str, Any]:
        """Returns monitoring data"""
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
        """Yield timeout to wait after unsuccessful RPC connection"""
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
        start_timestamp: float | None = None,
        cursor_id: str | None = None,
        auto_set_cursor: bool = True,
        async_cursor: bool = False,
        async_cursor_condition: asyncio.Condition | None = None,
    ) -> None:
        # @todo: Restart on failure
        async def set_cursor_sync(offset: int) -> None:
            """Synchronous version of cursor setter.
            Blocks until the cursor is really set.
            """
            await client.set_cursor(
                stream=stream,
                partition=partition,
                cursor_id=cursor_id,
                offset=offset,
            )

        async def set_cursor_async(offset: int) -> None:
            """Asynchronous version of cursor setter. Doesn't block subscriber loop,
            though committed cursor position may lag behind the really processed one.
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
                self.start_background_task(cursor_setter())
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
                        parent=span_id.decode() if span_id else None,
                        context=span_ctx.decode() if span_ctx else None,
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

    def _init_publisher(self) -> None:
        """Spin-up publisher and queue"""
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
        partition: int | None = None,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Schedule publish request"""
        if not self.publish_queue:
            self._init_publisher()
        req = MessageStreamClient.get_publish_request(
            data=value, stream=stream, partition=partition, sharding_key=key, headers=headers
        )
        self.publish_queue.put(req)

    async def publisher(self) -> None:
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

    async def shutdown_executors(self) -> None:
        if self.executors:
            self.logger.info("Shutting down executors")
            for x in self.executors:
                try:
                    self.logger.info("Shutting down %s", x)
                    await self.executors[x].shutdown()
                except TimeoutError:
                    self.logger.info("Timed out when shutting down %s", x)

    async def shutdown_subscriptions(self) -> None:
        self.logger.info("Shutting down subscriptions")
        self.subscriber_shutdown_waiter = asyncio.Event()
        try:
            await asyncio.wait_for(self.subscriber_shutdown_waiter.wait(), 10)
        except TimeoutError:
            self.logger.info(
                "Timed out when shutting down subscriptions. Some message may be still processing"
            )

    async def shutdown_publisher(self) -> None:
        if self.publish_queue:
            r = await self.publish_queue.drain(5.0)
            if not r:
                self.logger.info(
                    "Unclean shutdown of liftbridge queue. Up to %d messages may be lost",
                    self.publish_queue.qsize(),
                )
            self.publish_queue.shutdown()

    def get_executor(self, name: str) -> ThreadPoolExecutor:
        """Return or start named executor"""
        executor = self.executors.get(name)
        if not executor:
            xt = f"{self.name}.{name}_threads"
            max_threads = config.get_parameter(xt)
            self.logger.info(
                "Starting threadpool executor %s (up to %d threads)", name, max_threads
            )
            executor = ThreadPoolExecutor(max_threads, name=name)
            self.executors[name] = executor
        return executor

    def run_in_executor[T](
        self, name: str, fn: Callable[[Any], T], *args: Any, **kwargs: Any
    ) -> asyncio.Future:
        executor = self.get_executor(name)
        return executor.submit(fn, *args, **kwargs)

    async def message_route(self) -> None:
        """Route messages from mx_queue"""
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
        self, queue: QBuffer, headers: dict[str, bytes] | None = None
    ) -> None:
        """Schedule metrics to send stream

        Args:
            queue: Metrics Queue
            headers: Message Headers
        """
        while not (self.publish_queue.to_shutdown and queue.is_empty()):
            t0 = perf_counter()
            for stream, partition, chunk in queue.iter_slice():
                self.publish(chunk, stream=stream, partition=partition, headers=headers)
            if not self.publish_queue.to_shutdown:
                to_sleep = config.msgstream.metrics_send_delay - (perf_counter() - t0)
                if to_sleep > 0:
                    await asyncio.sleep(to_sleep)

    def register_metrics(self, table: str, metrics: list[dict[str, Any]], key: int | None = None):
        """Schedule metrics to be sent to the `table`.

        Args:
            table: Table name
            metrics: List of dicts containing metrics records
            key: Sharding key, None for round-robin distribution
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
        """Run telemetry callback"""
        self.telemetry_callback = PeriodicCallback(self.send_telemetry, 250)
        self.telemetry_callback.start()

    async def send_telemetry(self) -> None:
        """Publish telemetry data"""
        spans = get_spans()
        if spans:
            self.register_metrics("span", [span_to_dict(s) for s in spans])

    async def get_mx_routes_config(self) -> None:
        """Subscribe and track datastream changes"""
        client = RouteDataStreamClient("cfgmxroute", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track MX route settings")
            try:
                await client.query(limit=config.message.ds_limit, block=True)
            except NOCError as e:
                self.logger.info("Failed to get MX route settings: %s", e)
                await asyncio.sleep(1)

    async def update_route(self, data: dict[str, Any]) -> None:
        self.router.change_route(data)

    async def delete_route(self, r_id: str) -> None:
        self.router.delete_route(r_id)

    async def send_message(
        self,
        data: Any,
        message_type: MessageType,
        headers: dict[str, bytes] | None = None,
        sharding_key: int = 0,
        store: bool = False,
    ) -> None:
        """Build message and schedule to send to mx service

        Args:
            data: Data for transmit
            message_type: Message type
            headers: additional message headers
            sharding_key: Key for sharding over MX services
            store: Append message to buffer for deliver
        """
        msg = Router.get_message(data, message_type.value, headers, sharding_key)
        self.logger.debug("Send message: %s", msg)
        if not self.router and self.mx_partitions:
            self.publish(
                value=msg.value,
                stream=MX_STREAM,
                partition=sharding_key % self.mx_partitions,
                headers=msg.headers,
            )
            return
        if not self.router and not self.mx_partitions:
            self.logger.warning("Not MX service for forwarding message. Skipping...")
            return
        if store:
            self.mx_queue.put(msg)
        else:
            await self.router.route_message(msg)

    def register_message(
        self,
        data: Any,
        message_type: MessageType,
        headers: dict[str, bytes] | None = None,
        sharding_key: int = 0,
        group_key: str | None = None,
    ) -> None:
        """Register message for deliver

        Args:
            data: Data for transmit
            message_type: Message type
            headers: additional message headers
            sharding_key: Key for sharding over MX services
        """
        msg = Router.get_message(
            data,
            message_type.value,
            headers,
            sharding_key,
            raw_value=bool(group_key),
        )
        self.mx_queue.put(msg, group_key)

    def get_leader_lock_name(self) -> str | None:
        if self.leader_lock_name:
            return self.leader_lock_name % {"pool": config.pool}
        return None

    def is_valid_health_check(self, service_id: str) -> bool:
        """Check received service id matches own service id"""
        return not (
            self.dcs
            and self.dcs.health_check_service_id
            and self.dcs.health_check_service_id != service_id
        )

    def get_health_status(self) -> tuple[int, str]:
        """Check service health to be reported to service registry

        Returns:
            (http code, message)
        """
        if self.dcs and self.require_dcs_health:
            # DCS is initialized
            return self.dcs.get_status()
        return 200, "OK"

    def uptime(self) -> float:
        if not self.startup_ts:
            return 0
        return perf_counter() - self.startup_ts

    async def get_stream_partitions(self, stream: str) -> int:
        async with MessageStreamClient() as client:
            while True:
                meta = await client.fetch_metadata()
                if meta.metadata:
                    if stream in meta.metadata:
                        if meta.metadata[stream]:
                            return len(meta.metadata[stream])
                        break
                # Cluster election in progress or cluster is misconfigured
                self.logger.info(f"Stream '{stream}' has no active partitions. Waiting")
                await asyncio.sleep(1)

    @staticmethod
    @cachetools.cached(cachetools.TTLCache(maxsize=128, ttl=60), lock=dcs_slot_lock)
    def get_slot_limits(slot_name) -> int | None:
        """Get slot count
        Args:
            slot_name:
        """
        from noc.core.dcs.loader import get_dcs
        from noc.core.ioloop.util import run_sync

        dcs = get_dcs()
        return run_sync(partial(dcs.get_slot_limit, slot_name))

    async def on_route_rules_ready(self) -> None:
        """Called when all Router rules are ready."""
        return

    async def watchdog(self) -> None:
        """WatchDog task. View watchdog_waiter event, by setting /health API.
        If not set event - force reboot process
        """
        failed, delay, deviation = 0, config.watchdog.check_interval, 0.5
        while True:
            await asyncio.sleep(delay - deviation + 2 * deviation * random.random())
            self.logger.debug("WatchDog loop")
            if not self.watchdog_waiter.is_set() and failed > config.watchdog.failed_count:
                self.logger.warning("WatchDog is more %s failed. Deactivate process", failed)
                self.stop()
            elif not self.watchdog_waiter.is_set():
                failed += 1
                continue
            self.watchdog_waiter.clear()
            failed = 0
