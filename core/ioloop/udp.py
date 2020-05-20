# ----------------------------------------------------------------------
# Tornado IOLoop UDP socket
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import socket
from typing import Tuple, Optional
import asyncio
import errno


_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)


class UDPSocket(object):
    """
    UDP socket abstraction

    async def test():
        sock = UDPSocket()
        # Send request
        await sock.sendto(data, (address, port))
        # Wait reply
        data, addr = await sock.recvfrom(4096)
        # Close socket
        sock.close()
    """

    def __init__(self, tos: Optional[int] = None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if tos:
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)
        self.socket.setblocking(False)

    def __del__(self):
        self.close()

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    async def send_and_receive(
        self, data: bytes, address: Tuple[str, int]
    ) -> Tuple[bytes, Tuple[str, int]]:
        loop = asyncio.get_running_loop()
        fileno = self.socket.fileno()
        write_ev = asyncio.Event()
        loop.add_writer(fileno, write_ev.set)
        try:
            await write_ev.wait()
        finally:
            loop.remove_writer(fileno)
        self.socket.sendto(data, address)
        while True:
            read_ev = asyncio.Event()
            loop.add_reader(fileno, read_ev.set)
            try:
                await read_ev.wait()
            finally:
                loop.remove_reader(fileno)
            try:
                return self.socket.recvfrom(65536)
            except OSError as e:
                if e.errno in _ERRNO_WOULDBLOCK:
                    continue
                raise e


class UDPSocketContext(object):
    def __init__(self, sock: Optional[UDPSocket] = None, tos: Optional[int] = None):
        if sock:
            self.sock = sock
            self.to_close = False
        else:
            self.sock = UDPSocket(tos=tos)
            self.to_close = True

    def __enter__(self):
        return self.sock

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.to_close:
            self.sock.close()
            self.sock = None
