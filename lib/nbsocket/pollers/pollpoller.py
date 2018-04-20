# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## poll() poller class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import select
from errno import EBADF, EINTR
## NOC modules
from base import Poller
from noc.lib.debug import error_report


class PollPoller(Poller):
    def __init__(self):
        super(PollPoller, self).__init__()
        self.poll = select.poll()
        self.sockets = {}  # fileno -> socket
        self.readers = set()
        self.writers = set()

    def add_reader(self, sock):
        """
        Add reader to poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """
        if sock in self.readers:
            return
        f = sock.fileno()
        self.readers.add(sock)
        e = select.POLLIN
        if sock in self.writers:
            e |= select.POLLOUT
        self.poll.register(f, e)
        self.sockets[f] = sock

    def add_writer(self, sock):
        """
        Add writer to poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """
        if sock in self.writers:
            return
        f = sock.fileno()
        self.writers.add(sock)
        e = select.POLLOUT
        if sock in self.readers:
            e |= select.POLLIN
        self.poll.register(f, e)
        self.sockets[f] = sock

    def remove_reader(self, sock):
        """
        Remove reader from poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """
        if sock not in self.readers:
            return
        f = sock.fileno()
        e = 0
        if sock in self.writers:
            e |= select.POLLOUT
        self.poll.register(f, e)
        self.readers.remove(sock)
        if sock not in self.writers:
            del self.sockets[f]

    def remove_writer(self, sock):
        """
        Remove writer from poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """
        if sock not in self.writers:
            return
        f = sock.fileno()
        e = 0
        if sock in self.readers:
            e |= select.POLLIN
        self.poll.register(f, e)
        self.writers.remove(sock)
        if sock not in self.readers:
            del self.sockets[f]

    def get_active(self, timeout):
        """
        Returns a tuple of active [readers], [writers]
        :return:
        """
        try:
            events = self.poll.poll(timeout * 1000)  # s -> ms
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except Exception:
            return [], []
        # Build result
        rset = [
            self.sockets[fd]
            for fd, e in events
            if (e & (select.POLLIN | select.POLLHUP) and
                fd in self.sockets)
        ]
        wset = [
            self.sockets[fd]
            for fd, e in events
            if (e & select.POLLOUT and fd in self.sockets)
        ]
        return rset, wset
