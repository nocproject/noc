# ----------------------------------------------------------------------
# Asyncio UDP server
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import socket
from typing import Iterable, Tuple, Any


class UDPServerProtocol:
    def __init__(self, server):
        self._server = server

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # message = data #data.decode()
        # print('Received %r from %s' % (message, addr))
        self._server.on_read(data, addr)

    def error_received(self, exc):
        # print('Received error %s' % exc)
        pass


class UDPServer(object):
    def iter_listen(self, cfg: str) -> Iterable[Tuple[str, int]]:
        """
        Parses listen configuration and yield (address, port) tuples.
        Listen configuration is comma-separated string with items:
        * address:port
        * port

        :param cfg:
        :return:
        """
        for listen in cfg.split(","):
            listen = listen.strip()
            if ":" in listen:
                addr, port = listen.split(":")
            else:
                addr, port = "", listen
            yield addr, int(port)

    async def listen(self, port: int, address: str = "") -> None:
        await self.bind_udp_sockets(port, address=address)

    def start(self):
        pass

    def on_read(self, data: bytes, address: Tuple[str, int]):
        """
        To be overriden
        """

    async def bind_udp_sockets(
        self, port, address: str = None, family: int = socket.AF_UNSPEC, flags: Any = None
    ):
        if address == "":
            address = None
        if flags is None:
            flags = socket.AI_PASSIVE

        loop = asyncio.get_running_loop()
        for res in set(socket.getaddrinfo(address, port, family, socket.SOCK_DGRAM, 0, flags)):
            # print("*** res", res, type(res))
            af, socktype, proto, canonname, sockaddr = res
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPServerProtocol(self), local_addr=(sockaddr[0], sockaddr[1])
            )
