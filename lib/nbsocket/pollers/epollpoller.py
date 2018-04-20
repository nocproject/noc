# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## epoll poller class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import select
## NOC modules
from base import Poller
from noc.lib.debug import error_report
from errno import EBADF, EINTR


class EpollPoller(Poller):
    def __init__(self):
        super(EpollPoller, self).__init__()
        self.sockets = {}  # fileno -> socket
        self.readers = set()
        self.writers = set()
        self.epoll = select.epoll()

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
        if sock in self.writers:
            self.epoll.modify(f, select.EPOLLIN | select.EPOLLOUT)
        else:
            self.epoll.register(f, select.EPOLLIN)
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
        if sock in self.readers:
            self.epoll.modify(f, select.EPOLLIN | select.EPOLLOUT)
        else:
            self.epoll.register(f, select.EPOLLOUT)
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
        if sock in self.writers:
            self.epoll.modify(f, select.EPOLLOUT)
        else:
            self.epoll.unregister(f)
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
        if sock in self.readers:
            self.epoll.modify(f, select.EPOLLIN)
        else:
            self.epoll.unregister(f)
        self.writers.remove(sock)
        if sock not in self.readers:
            del self.sockets[f]

    def get_active(self, timeout):
        """
        Returns a tuple of active [readers], [writers]
        :return:
        """
        try:
            events = self.epoll.poll(timeout)  # s -> ms
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
            if (e & (select.EPOLLIN | select.EPOLLHUP) and
                fd in self.sockets)
        ]
        wset = [
            self.sockets[fd]
            for fd, e in events
            if (e & select.EPOLLOUT and fd in self.sockets)
        ]
        return rset, wset
