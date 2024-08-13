# ----------------------------------------------------------------------
# Asyncio UDP server
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import errno
import logging
import os
import platform
import socket
import sys
from typing import Iterable, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server):
        super().__init__()
        self._server = server

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self._server.on_read(data, addr)

    def error_received(self, exc):
        logger.error("UDP server received error %s" % exc)


class UDPServer(object):
    def __init__(self):
        self._transports: List[asyncio.BaseTransport] = []
        self._sockaddr: List[Tuple[str, int]] = []

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
        sockets = self.bind_udp_sockets(port, address=address)
        await self.create_endpoints(sockets)

    def start(self):
        pass

    def stop(self):
        for transport in self._transports:
            transport.close()

    def on_read(self, data: bytes, address: Tuple[str, int]):
        """
        To be overriden
        """

    async def create_endpoints(self, sockets):
        loop = asyncio.get_running_loop()
        for sock in sockets:
            transport, _ = await loop.create_datagram_endpoint(
                lambda: UDPServerProtocol(self), sock=sock
            )
            self._transports.append(transport)

    def bind_udp_sockets(
        self,
        port: int,
        address: Optional[str] = None,
        family: int = socket.AF_UNSPEC,
        flags: Any = None,
    ):
        """Creates listening sockets bound to the given port and address.

        Returns a list of socket objects (multiple sockets are returned if
        the given address maps to multiple IP addresses, which is most common
        for mixed IPv4 and IPv6 use).

        Address may be either an IP address or hostname.  If it's a hostname,
        the server will listen on all IP addresses associated with the
        name.  Address may be an empty string or None to listen on all
        available interfaces.  Family may be set to either `socket.AF_INET`
        or `socket.AF_INET6` to restrict to IPv4 or IPv6 addresses, otherwise
        both will be used if available.

        The ``backlog`` argument has the same meaning as for
        `socket.listen() <socket.socket.listen>`.

        ``flags`` is a bitmask of AI_* flags to `~socket.getaddrinfo`, like
        ``socket.AI_PASSIVE | socket.AI_NUMERICHOST``.
        """
        sockets = []
        if address == "":
            address = None
        if not socket.has_ipv6 and family == socket.AF_UNSPEC:
            # Python can be compiled with --disable-ipv6, which causes
            # operations on AF_INET6 sockets to fail, but does not
            # automatically exclude those results from getaddrinfo
            # results.
            # http://bugs.python.org/issue16208
            family = socket.AF_INET
        if flags is None:
            flags = socket.AI_PASSIVE
        bound_port = None
        for res in set(socket.getaddrinfo(address, port, family, socket.SOCK_DGRAM, 0, flags)):
            af, socktype, proto, canonname, sockaddr = res
            if (
                platform.system() == "Darwin"
                and address == "localhost"
                and af == socket.AF_INET6
                and sockaddr[3] != 0
            ):
                # Mac OS X includes a link-local address fe80::1%lo0 in the
                # getaddrinfo results for 'localhost'.  However, the firewall
                # doesn't understand that this is a local address and will
                # prompt for access (often repeatedly, due to an apparent
                # bug in its ability to remember granting access to an
                # application). Skip these addresses.
                continue
            try:
                sock = socket.socket(af, socktype, proto)
            except OSError as e:
                if e.args[0] == errno.EAFNOSUPPORT:
                    continue
                raise
            if os.name != "nt":
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if af == socket.AF_INET6:
                # On linux, ipv6 sockets accept ipv4 too by default,
                # but this makes it impossible to bind to both
                # 0.0.0.0 in ipv4 and :: in ipv6.  On other systems,
                # separate sockets *must* be used to listen for both ipv4
                # and ipv6.  For consistency, always disable ipv4 on our
                # ipv6 sockets and use a separate ipv4 socket when needed.
                #
                # Python 2.x on windows doesn't have IPPROTO_IPV6.
                if hasattr(socket, "IPPROTO_IPV6"):
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)

            # automatic port allocation with port=None
            # should bind on the same port on IPv4 and IPv6
            host, requested_port = sockaddr[:2]
            if requested_port == 0 and bound_port is not None:
                sockaddr = tuple([host, bound_port] + list(sockaddr[2:]))

            sock.setblocking(False)
            self.setup_socket(sock)
            sock.bind(sockaddr)
            sa = sock.getsockname()
            bound_port = sa[1]
            self._sockaddr.append(sa)
            sockets.append(sock)
        return sockets

    def enable_reuseport(self) -> bool:
        """
        Override if SO_REUSEPORT should be set
        :return:
        """
        return False

    def enable_freebind(self) -> bool:
        """
        Override if IP_FREEBIND should be set
        :return:
        """
        return True

    @property
    def has_reuseport(self) -> bool:
        return hasattr(socket, "SO_REUSEPORT")

    @property
    def has_frebind(self) -> bool:
        return self.get_ip_freebind() is not None

    def setup_socket(self, sock: "socket"):
        """
        Called after socket created but before .bind().
        Can be overriden to adjust socket options in superclasses
        :param sock: socket instance
        :return: None
        """
        # Set SO_REUSEPORT option
        if self.has_reuseport and self.enable_reuseport():
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Set IP_FREEBIND option
        if self.has_frebind and self.enable_freebind():
            sock.setsockopt(socket.SOL_IP, self.get_ip_freebind(), 1)

    def get_ip_freebind(self) -> Optional[int]:
        """
        Many python distributions does not include IP_FREEBIND to socket module
        :return: IP_FREEBIND value or None
        """
        if hasattr(socket, "IP_FREEBIND"):
            # Valid distribution
            return socket.IP_FREEBIND
        if sys.platform == "linux2":
            return 15
        return None
