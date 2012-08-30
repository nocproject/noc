# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## kevent/kqueue poller class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import select
from errno import EINTR
## NOC modules
from base import Poller


class KEventPoller(Poller):
    def __init__(self):
        super(KEventPoller, self).__init__()
        self.sockets = {}  # fileno -> socket
        self.readers = set()
        self.writers = set()
        self.kqueue = select.kqueue()

    def _update(self, f, filter, op):
        """
        Update socket's kqueue registration
        :param f: file handler
        :param filter: KQ_FILTER_READ or KQ_FILTER_WRITE
        :param op: KQ_EV_ADD or KQ_EV_DELETE
        :return:
        """
        self.kqueue.control([select.kevent(f, filter, op)], 0)

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
        self._update(f, select.KQ_FILTER_READ, select.KQ_EV_ADD)
        self.readers.add(sock)
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
        self._update(f, select.KQ_FILTER_WRITE, select.KQ_EV_ADD)
        self.writers.add(sock)
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
        self._update(f, select.KQ_FILTER_READ, select.KQ_EV_DELETE)
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
        self._update(f, select.KQ_FILTER_WRITE, select.KQ_EV_DELETE)
        self.writers.remove(sock)
        if sock not in self.readers:
            del self.sockets[f]

    def get_active(self, timeout):
        """
        Returns a tuple of active [readers], [writers]
        :return:
        """
        rset = []
        wset = []
        l = len(self.readers) + len(self.writers)
        try:
            events = self.kqueue.control(None, l, timeout)
        except OSError, e:
            if e[0] == EINTR:
                return [], []  # Interrupted system call
            else:
                raise
        for e in events:
            s = self.sockets.get(e.ident)
            if s is None:
                continue
            if e.filter == select.KQ_FILTER_WRITE:
                wset += [s]
            if e.filter == select.KQ_FILTER_READ:
                rset += [s]
        return rset, wset
