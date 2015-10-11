# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tornado IOLoop UDP socket
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import errno
import socket
## Third-party modules
from tornado.ioloop import IOLoop
from tornado.concurrent import TracebackFuture
from tornado.util import errno_from_exception


_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)


class UDPSocket(object):
    """
    UDP socket abstraction

    @tornado.gen.coroutine
    def test():
        sock = UDPSocket()
        # Send request
        yield sock.sendto(data, (address, port))
        # Wait reply
        data, addr = yield sock.recvfrom(4096)
        # Close socket
        sock.close()
    """
    def __init__(self, ioloop=None):
        self.ioloop = ioloop or IOLoop.current()
        self.send_buffer = None  # (data, address)
        self.bufsize = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.fd = self.socket.fileno()
        self.socket.setblocking(0)
        self.future = None
        self.timeout = None
        self.timeout_task = None
        self.events = None

    def __del__(self):
        self.close()

    def get_future(self):
        """
        Get future and start timeout task when needed
        """
        if not self.future or self.future.done():
            self.future = TracebackFuture()
            self.start_timeout()
        return self.future

    def settimeout(self, timeout):
        """
        Set timeout for following blocking operations
        """
        self.stop_timeout()
        self.timeout = timeout

    def start_timeout(self):
        self.stop_timeout()
        if self.timeout:
            self.timeout_task = self.ioloop.call_later(
                self.timeout,
                self.on_timeout
            )

    def stop_timeout(self):
        if self.timeout_task:
            self.ioloop.remove_timeout(self.timeout_task)
            self.timeout_task = None

    def add_handler(self, callback, events):
        self.remove_handler()
        self.ioloop.add_handler(self.fd, callback, events)
        self.events = events

    def remove_handler(self):
        if self.events:
            self.ioloop.remove_handler(self.fd)
            self.events = 0

    def recvfrom(self, bufsize):
        future = self.get_future()
        try:
            data, addr = self.socket.recvfrom(bufsize)
            self.remove_handler()
            future.set_result((data, addr))
        except socket.error as e:
            c = errno_from_exception(e)
            if c in _ERRNO_WOULDBLOCK:
                self.bufsize = bufsize
                self.add_handler(self.on_read, IOLoop.READ)
            else:
                future.set_exception()
        return future

    def sendto(self, data, address):
        future = self.get_future()
        try:
            r = self.socket.sendto(data, address)
            self.remove_handler()
            future.set_result(r)
        except socket.error as e:
            c = errno_from_exception(e)
            if c in _ERRNO_WOULDBLOCK:
                # Wait for socket is ready to write
                self.send_buffer = (data, address)
                self.add_handler(self.on_write, IOLoop.WRITE)
            else:
                future.set_exception(e)
        return future

    def on_read(self, fd, events):
        self.recvfrom(self.bufsize)

    def on_write(self, fd, events):
        self.ioloop.remove_handler(self.fd)
        data, address = self.send_buffer
        self.send_buffer = None
        self.sendto(data, address)

    def on_timeout(self):
        if self.future and self.future.running():
            self.timeout_task = None
            try:
                raise socket.timeout()
            except Exception as e:
                self.future.set_exception(e)

    def close(self):
        if self.timeout_task:
            self.ioloop.remove_timeout(self.timeout_task)
            self.timeout_task = None
        if self.socket:
            self.remove_handler()
            self.socket.close()
            self.socket = None
