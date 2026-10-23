# ----------------------------------------------------------------------
# SessionStore
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from dataclasses import dataclass
import asyncio
from contextlib import suppress

# NOC modules
from noc.core.service.loader import get_service
from .cli.base import BaseCLI


@dataclass
class Session:
    session: str
    stream: BaseCLI
    timer_task: asyncio.Handle | None = None


class SessionStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: dict[str, Session] = {}
        self._loop: asyncio.BaseEventLoop | None = None

    def get(self, session: str) -> BaseCLI | None:
        with self._lock:
            item = self._sessions.get(session)
            if item is None:
                return None
            # Delete from store to prevent session hijacking
            # del self._sessions[session]
            self._set_timer(item, None)
            if item.stream.is_closed():
                return None
            return item.stream

    def remove(self, session: str, shutdown: bool = False):
        with self._lock:
            item = self._sessions.get(session)
            if not item:
                return
            if not shutdown:
                del self._sessions[session]
            self._set_timer(item, None)
        if not item.stream.is_closed():
            if shutdown:
                with suppress(Exception):
                    # Under all conditions Session be removed
                    item.stream.shutdown_session()
            with self._lock:
                del self._sessions[session]
            item.stream.close()

    def put(self, session: str, stream: BaseCLI, timeout: int | None = None):
        with self._lock:
            item = self._sessions.get(session)
            if item:
                item.stream = stream
            else:
                item = Session(session=session, stream=stream)
                self._sessions[session] = item
            self._set_timer(item, timeout)

    async def _timer_task(self, session: str, timeout: float):
        # Running on main service's event loop
        try:
            await asyncio.sleep(timeout)
        except asyncio.CancelledError:
            return
        with self._lock:
            item = self._sessions.get(session)
            if not item:
                return
            del self._sessions[session]
        if not item.stream.is_closed():
            item.stream.close()

    def _set_timer(self, item: Session, timer: int | None = None):
        def _run_timer(session: str, t: int | None):
            # Running on main service's event loop
            with self._lock:
                i = self._sessions.get(session)
                if not i:
                    return
                if i.timer_task:
                    i.timer_task.cancel()
                if t:
                    i.timer_task = asyncio.create_task(self._timer_task(session, t))

        loop = get_service().get_event_loop()
        if not loop:
            raise RuntimeError("Event Loop is not running")
        if item.timer_task is not None or timer:
            loop.call_soon_threadsafe(_run_timer, item.session, timer)
