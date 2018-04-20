# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## select() poller class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import select
import sys
import logging
from errno import EBADF, EINTR
## NOC modules
from base import Poller
from noc.lib.debug import error_report


class SelectPoller(Poller):
    def __init__(self):
        super(SelectPoller, self).__init__()
        self.sockets = {}  # fileno -> socket
        self.readers = set()
        self.writers = set()
        self.rset = []
        self.wset = []

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
        self.rset += [f]
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
        self.wset += [f]
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
        self.rset.remove(f)
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
        self.wset.remove(f)
        self.writers.remove(sock)
        if sock not in self.readers:
            del self.sockets[f]

    def get_active(self, timeout):
        """
        Returns a tuple of active [readers], [writers]
        :return:
        """
        try:
            r, w, x = select.select(self.rset, self.wset, [], timeout)
            rset = [self.sockets[x] for x in r if x in self.sockets]
            wset = [self.sockets[x] for x in w if x in self.sockets]
            return rset, wset
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except KeyboardInterrupt:
            logging.info("Got Ctrl+C, exiting")
            sys.exit(0)
        except Exception:
            error_report()
            return [], []
