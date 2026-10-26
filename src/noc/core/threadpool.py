# ----------------------------------------------------------------------
# ThreadPool class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""Manage a bounded pool of threads for asynchronous task submission.

Submitted callables run in worker threads, and their results or exceptions are
delivered through :class:`asyncio.Future` instances.
"""

# Python modules
import _thread
import asyncio
import itertools
import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from time import perf_counter
from types import TracebackType
from typing import Any, NamedTuple, Self

# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.span import Span, get_current_span

logger = logging.getLogger(__name__)

DEFAULT_IDLE_TIMEOUT = config.threadpool.idle_timeout
DEFAULT_SHUTDOWN_TIMEOUT = config.threadpool.shutdown_timeout


class WorkerTask(NamedTuple):
    """Describe one callable queued for execution by a worker.

    Attributes:
        future: Future completed with the callable's result or exception.
        fn: Callable to execute.
        args: Positional arguments passed to ``fn``.
        kwargs: Keyword arguments passed to ``fn``.
        span_ctx: Trace context identifier captured when the task was
            submitted.
        span: Parent span identifier captured when the task was submitted.
        in_label: Optional label or label factory for forensic tracing.
    """

    future: asyncio.Future[Any]
    fn: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    span_ctx: int | None
    span: int | None
    in_label: Any


class ThreadPoolExecutor:
    """Run submitted callables in a pool of at most ``max_workers`` threads.

    Worker threads are started as tasks arrive and may exit after remaining
    idle for ``idle_timeout`` seconds. The executor can also be used as a
    context manager to stop its workers when the context exits.
    """

    def __init__(
        self,
        max_workers: int,
        idle_timeout: int = DEFAULT_IDLE_TIMEOUT,
        shutdown_timeout: int = DEFAULT_SHUTDOWN_TIMEOUT,
        name: str | None = None,
    ) -> None:
        """Initialize the thread pool.

        Args:
            max_workers: Maximum number of worker threads.
            idle_timeout: Seconds a worker waits without a task before exiting.
                A value of zero disables the idle timeout.
            shutdown_timeout: Seconds to wait for workers during shutdown. A
                value of zero disables the shutdown timeout.
            name: Prefix used for metrics associated with this pool.
        """
        self.max_workers = max_workers
        self.threads: set[threading.Thread] = set()
        self.mutex = threading.Lock()
        self.queue: deque[WorkerTask | None] = deque()
        self.to_shutdown = False
        self.idle_timeout = idle_timeout or None
        self.shutdown_timeout = shutdown_timeout or None
        self.submitted_tasks = 0
        self.worker_id = itertools.count()
        self.name = name or "threadpool"
        self.done_event: threading.Event | None = None
        self.done_future: asyncio.Future[bool] | None = None
        self.started = perf_counter()
        self.waiters: list[_thread.LockType] = []
        if config.thread_stack_size:
            threading.stack_size(config.thread_stack_size)

    def __enter__(self) -> Self:
        """Return this executor for use in a ``with`` statement.

        Returns:
            This executor.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Stop workers when leaving a context manager.

        Exceptions raised in the context are not suppressed.

        Args:
            exc_type: Exception type raised in the context, if any.
            exc_val: Exception raised in the context, if any.
            exc_tb: Traceback for the context exception, if any.
        """
        if not self.to_shutdown:
            if exc_type:
                # Stop workers and raise error
                self._stop_workers()
            else:
                # Graceful shutdown
                self.shutdown(sync=True)

    def _put(self, item: WorkerTask) -> None:
        """Enqueue a task and start or wake a worker as needed.

        Args:
            item: Task to append to the work queue.
        """
        with self.mutex:
            if not len(self.waiters) and len(self.threads) < self.max_workers:
                # Start new thread
                name = f"worker-{next(self.worker_id)}"
                t = threading.Thread(target=self.worker, name=name)
                t.daemon = True
                self.threads.add(t)
                t.start()
            # Enqueue task
            self.queue.append(item)
            self.submitted_tasks += 1
            if self.waiters:
                e = self.waiters.pop(0)
                e.release()

    def _get(self, timeout: float | None) -> WorkerTask | None:
        """Wait for and remove the next queued task.

        Args:
            timeout: Maximum idle wait in seconds, or ``None`` to wait
                indefinitely.

        Returns:
            The next task, or ``None`` when a worker stop signal is queued.

        Raises:
            IdleTimeout: If no task arrives before ``timeout`` expires.
        """
        e = None
        endtime = None
        while True:
            with self.mutex:
                if self._qsize():
                    return self.queue.popleft()
                # Waiting lock
                if not e:
                    e = _thread.allocate_lock()
                    e.acquire()
                self.waiters.insert(0, e)
            # Wait for condition or timeout
            t = perf_counter()
            if endtime is None and timeout is not None:
                endtime = t + timeout
            delay = 0.0005
            while True:
                ready = e.acquire(False)
                if ready:
                    break
                remaining = endtime - t if endtime is not None else 0.05
                if endtime is not None and remaining <= 0.0:
                    try:
                        self.waiters.remove(e)
                    except ValueError:
                        pass
                    raise IdleTimeout()
                delay = min(delay * 2, remaining, 0.05)
                time.sleep(delay)
                t = perf_counter()

    def _qsize(self) -> int:
        """Return the number of items currently in the work queue.

        Returns:
            Queue length, including any worker stop signals.
        """
        return len(self.queue)

    def set_max_workers(self, max_workers: int) -> None:
        """Set the worker limit, stopping excess workers when it decreases.

        Increasing the limit does not start workers immediately; they start
        when tasks are submitted.

        Args:
            max_workers: New maximum number of worker threads.
        """
        stop_count = 0
        with self.mutex:
            if max_workers < self.max_workers:
                # Reduce pool
                tl = len(self.threads)
                if tl > max_workers:
                    stop_count = tl - max_workers
            self.max_workers = max_workers
        if stop_count:
            self._stop_workers(stop_count)

    def _stop_workers(self, n: int = 0) -> None:
        """Queue stop signals for workers and wake idle workers.

        Args:
            n: Number of stop signals to enqueue. If zero, enqueue one for
                each currently running worker.
        """
        with self.mutex:
            if not n:
                n = len(self.threads)
            for _ in range(n):
                self.queue.append(None)
                if self.waiters:
                    self.waiters.pop(0).release()

    def submit[T](self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> asyncio.Future[T]:
        """Schedule a callable on a worker thread.

        The special ``_in_label`` keyword, if present, is consumed by the
        executor and used as a tracing label rather than passed to ``fn``.

        Args:
            fn: Callable to run in a worker thread.
            *args: Positional arguments passed to ``fn``.
            **kwargs: Keyword arguments passed to ``fn``, except ``_in_label``.

        Returns:
            A future that receives the callable's result or exception.

        Raises:
            RuntimeError: If the executor has started shutting down.
        """
        if self.to_shutdown:
            raise RuntimeError("Cannot schedule new task after shutdown")
        future: asyncio.Future[T] = asyncio.Future()
        span_ctx, span = get_current_span()
        # Fetch span label
        if "_in_label" in kwargs:
            in_label = kwargs.pop("_in_label")
        else:
            in_label = None
        # Put to the working queue
        self._put(WorkerTask(future, fn, args, kwargs, span_ctx, span, in_label))
        return future

    def shutdown(self, sync: bool = False) -> asyncio.Future[bool]:
        """Stop all workers and return a future for pool termination.

        Args:
            sync: If true, block for up to ``shutdown_timeout`` before
                returning. If false, return immediately with a future that
                waits asynchronously for termination.

        Returns:
            A future that resolves to true when all workers have terminated.
                In synchronous mode the returned future may still be pending
                if the timeout expires before termination.
        """
        logger.info("Shutdown")
        done_future: asyncio.Future[bool] = asyncio.Future()
        done_event = threading.Event() if sync else None
        with self.mutex:
            self.done_future = done_future
            if done_event is not None:
                self.done_event = done_event
            self.to_shutdown = True
        self._stop_workers()
        logger.info("Waiting for workers")
        if done_event is not None:
            done_event.wait(timeout=self.shutdown_timeout)
            return done_future
        return asyncio.ensure_future(asyncio.wait_for(done_future, self.shutdown_timeout))

    @staticmethod
    def _set_future_result(future: asyncio.Future[Any], result: Any) -> None:
        """Set a future's result on its event loop from a worker thread.

        Args:
            future: Future to complete.
            result: Result value to assign to the future.
        """
        future.get_loop().call_soon_threadsafe(future.set_result, result)

    @staticmethod
    def _set_future_exception(future: asyncio.Future[Any], exc: BaseException) -> None:
        """Set a future's exception on its event loop from a worker thread.

        Args:
            future: Future to complete.
            exc: Exception to assign to the future.
        """
        future.get_loop().call_soon_threadsafe(future.set_exception, exc)

    def worker(self) -> None:
        """Run queued tasks until stopped or the idle timeout expires."""
        t = threading.current_thread()
        logger.debug("Starting worker thread %s", t.name)
        try:
            while not self.to_shutdown:
                try:
                    task = self._get(self.idle_timeout)
                except IdleTimeout:
                    logger.debug("Closing idle thread")
                    break
                if task is None:
                    logger.debug("Worker %s received stop signal", t.name)
                    break
                future, fn, args, kwargs, span_ctx, span, in_label = task
                # if not future.set_running_or_notify_cancel():
                #     continue
                sample = 1 if span_ctx else 0
                if config.features.forensic:
                    if in_label and callable(in_label):
                        in_label = in_label(*args, **kwargs)
                    in_label = in_label or str(fn)
                else:
                    in_label = None
                with Span(
                    service="threadpool",
                    sample=sample,
                    context=span_ctx,
                    parent=span,
                    in_label=in_label,
                ) as span:
                    try:
                        result = fn(*args, **kwargs)
                        self._set_future_result(future, result)
                        result = None  # Release memory
                    except NOCError as e:
                        self._set_future_exception(future, e)
                        span.set_error_from_exc(e, e.default_code)
                    except BaseException as e:
                        self._set_future_exception(future, e)
                        span.set_error_from_exc(e)
        finally:
            logger.debug("Stopping worker thread %s", t.name)
            with self.mutex:
                self.threads.remove(t)
                if self.to_shutdown and not len(self.threads):
                    logger.info("ThreadPool terminated")
                    if self.done_event:
                        self.done_event.set()
                    if self.done_future:
                        self.done_future.set_result(True)

    def may_submit(self) -> bool:
        """Check whether the pool can accept a task without exceeding limits.

        Returns:
            True if a worker is idle or another worker can be started;
            otherwise, false. Returns false after shutdown begins.
        """
        with self.mutex:
            return not self.to_shutdown and (
                (self._qsize() < len(self.waiters)) or (self.max_workers > len(self.threads))
            )

    def get_free_workers(self) -> int:
        """Estimate how many tasks can be submitted without waiting.

        Returns:
            Available worker capacity after accounting for running workers,
            queued tasks, and idle workers. Returns zero after shutdown begins.
        """
        with self.mutex:
            if self.to_shutdown:
                return 0
            return max(
                (self.max_workers - len(self.threads) - self._qsize() + len(self.waiters)), 0
            )

    def apply_metrics(self, d: dict[str, Any]) -> None:
        """Add this pool's metrics to a dictionary.

        Args:
            d: Dictionary to update with worker counts, queue size, submitted
                task count, and uptime. Metric keys use the pool's name prefix.
        """
        with self.mutex:
            workers = len(self.threads)
            idle = len(self.waiters)
            d.update(
                {
                    f"{self.name}_max_workers": self.max_workers,
                    f"{self.name}_workers": workers,
                    f"{self.name}_idle_workers": idle,
                    f"{self.name}_running_workers": workers - idle,
                    f"{self.name}_submitted_tasks": self.submitted_tasks,
                    f"{self.name}_queued_jobs": len(self.queue),
                    f"{self.name}_uptime": perf_counter() - self.started,
                }
            )


class IdleTimeout(Exception):
    """Signal that a worker has waited too long for a task."""
