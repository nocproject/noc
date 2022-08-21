# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
import asyncio
import contextlib
from typing import Optional

# NOC modules
from noc.config import config
from .base import BaseCLI


class BaseStream(object):
    default_port = 23
    # compiled capabilities
    HAS_TCP_KEEPALIVE = hasattr(socket, "SO_KEEPALIVE")
    HAS_TCP_KEEPIDLE = hasattr(socket, "TCP_KEEPIDLE")
    HAS_TCP_KEEPINTVL = hasattr(socket, "TCP_KEEPINTVL")
    HAS_TCP_KEEPCNT = hasattr(socket, "TCP_KEEPCNT")
    HAS_TCP_NODELAY = hasattr(socket, "TCP_NODELAY")
    # Time until sending first keepalive probe
    KEEP_IDLE = 10
    # Keepalive packets interval
    KEEP_INTVL = 10
    # Terminate connection after N keepalive failures
    KEEP_CNT = 3

    def __init__(self, cli: BaseCLI):
        self._timeout: Optional[float] = None
        self.logger = cli.logger
        self.tos = cli.tos
        self.socket: Optional[socket.socket] = None
        self.connect_timeout: float = config.activator.connect_timeout

    async def connect(
        self, address: str, port: Optional[int] = None, timeout: Optional[float] = None
    ):
        """
        Process connection sequence
        :param address:
        :param port:
        :param timeout:
        :return:
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.tos:
            self.logger.debug("Setting IP ToS to %d", self.tos)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, self.tos)
        if self.HAS_TCP_NODELAY:
            self.logger.info("Setting TCP NODELAY")
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self.HAS_TCP_KEEPALIVE:
            self.logger.info("Settings KEEPALIVE")
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if self.HAS_TCP_KEEPIDLE:
                self.logger.info("Setting TCP KEEPIDLE to %d", self.KEEP_IDLE)
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.KEEP_IDLE)
            if self.HAS_TCP_KEEPINTVL:
                self.logger.info("Setting TCP KEEPINTVL to %d", self.KEEP_INTVL)
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.KEEP_INTVL)
            if self.HAS_TCP_KEEPCNT:
                self.logger.info("Setting TCP KEEPCNT to %d", self.KEEP_CNT)
                self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, self.KEEP_CNT)
        self.socket.setblocking(False)
        loop = asyncio.get_running_loop()
        self.set_timeout(timeout or self.connect_timeout)
        try:
            await asyncio.wait_for(
                loop.sock_connect(self.socket, (address, port or self.default_port)), self._timeout
            )
        except OSError:
            raise ConnectionRefusedError

    async def startup(self):
        """
        Setup connection after startup
        :return:
        """

    async def wait_for_read(self):
        """
        Wait until data available for read
        :return:
        """
        if not self.socket:
            self.logger.warning("Wait for READ: No Socket Ready")
            return
        loop = asyncio.get_running_loop()
        read_ev = asyncio.Event()
        fileno = self.socket.fileno()
        loop.add_reader(fileno, read_ev.set)
        try:
            await asyncio.wait_for(read_ev.wait(), self._timeout)
        finally:
            loop.remove_reader(fileno)

    async def wait_for_write(self):
        """
        Wait until socket will be available for write
        :return:
        """
        if not self.socket:
            return
        loop = asyncio.get_running_loop()
        write_ev = asyncio.Event()
        fileno = self.socket.fileno()
        loop.add_writer(fileno, write_ev.set)
        try:
            await asyncio.wait_for(write_ev.wait(), self._timeout)
        finally:
            loop.remove_writer(fileno)

    async def read(self, n: int) -> bytes:
        """
        Read up to n bytes from socket.
        Return empty bytes on EOF
        :param n:
        :return:
        """
        await self.wait_for_read()
        try:
            return self.socket.recv(n)
        except ConnectionResetError:
            self.logger.debug("Connection reset")
            raise asyncio.TimeoutError

    async def write(self, data: bytes):
        """
        Write data to socket
        :param data:
        :return:
        """
        while data:
            await self.wait_for_write()
            try:
                sent = self.socket.send(data)
            except OSError as e:
                self.logger.debug("Failed to write: %s", e)
                raise asyncio.TimeoutError()
            data = data[sent:]

    def close(self):
        # On SSH close call when 'SSH session reset' and if call stream.close second - socket is None
        # Check socket exists before close.
        if self.socket:
            self.socket.close()
            self.socket = None

    def set_timeout(self, timeout: Optional[float] = None):
        self._timeout = timeout

    @contextlib.contextmanager
    def timeout(self, timeout: Optional[float] = None):
        old_timeout = self.timeout
        self.set_timeout(timeout)
        yield
        self.set_timeout(old_timeout)
