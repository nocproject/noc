# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## nbsocket factory
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
import select
import time
import sys
from threading import RLock
from errno import EBADF, EINTR
## NOC modules
from noc.lib.debug import error_report
from noc.lib.nbsocket.exceptions import get_socket_error
from noc.lib.nbsocket.listentcpsocket import ListenTCPSocket
from noc.lib.nbsocket.connectedtcpsocket import ConnectedTCPSocket
from noc.lib.nbsocket.acceptedtcpsocket import AcceptedTCPSocket


class SocketFactory(object):
    """
    Socket factory is a major event loop controller, maintaining full socket
    lifetime
    """
    def __init__(self, tick_callback=None, polling_method=None, controller=None):
        self.sockets = {}      # fileno -> socket
        self.socket_name = {}  # socket -> name
        self.name_socket = {}  # name -> socket
        self.new_sockets = []  # list of (socket,name)
        self.tick_callback = tick_callback
        self.to_shutdown = False
        self.register_lock = RLock()    # Guard for register/unregister operations
        self.controller = controller    # Reference to controlling daemon
        self.get_active_sockets = None  # Polling method
        self.setup_poller(polling_method)
        # Performance data
        self.cnt_polls = 0  # Number of polls

    def shutdown(self):
        """
        Shut down socket factory and exit next event loop
        """
        logging.info("Shutting down the factory")
        self.to_shutdown = True

    # Check select() available
    def has_select(self):
        """
        Check select() method is available

        :rtype: Bool
        """
        return True

    def has_kevent(self):
        """
        Check kevent/kqueue method is available

        :rtype: Bool
        """
        return hasattr(select, "kqueue")

    def has_poll(self):
        """
        Check poll() method is available

        :rtype: Bool
        """
        return hasattr(select, "poll")

    def has_epoll(self):
        """
        Check epoll() method is available

        :rtype: Bool
        """
        return hasattr(select, "epoll")

    def setup_poller(self, polling_method=None):
        """
        Set up polling function.

        :param polling_method: Name of polling method. Must be one of:
                               * select
                               * poll
                               * kevent
                               * epoll
                               * None (detect best method)
        """
        def setup_select_poller():
            """Enable select() method"""
            logging.debug("Set up select() poller")
            self.get_active_sockets = self.get_active_select
            self.polling_method = "select"

        def setup_poll_poller():
            """Enable poll() method"""
            logging.debug("Set up poll() poller")
            self.get_active_sockets = self.get_active_poll
            self.polling_method = "poll"

        def setup_epoll_poller():
            """Enable epoll() method"""
            logging.debug("Set up epoll() poller")
            self.get_active_sockets = self.get_active_epoll
            self.polling_method = "epoll"

        def setup_kevent_poller():
            """Enable kevent() method. Broken for now and disabled"""
            logging.debug("Set up kevent/kqueue poller")
            self.get_active_sockets = self.get_active_kevent
            self.polling_method = "kevent"

        if polling_method is None:
            # Read settings if available
            try:
                from noc.settings import config
                polling_method = config.get("main", "polling_method")
            except ImportError:
                polling_method = "select"
        logging.debug("Setting up '%s' polling method" % polling_method)
        if polling_method == "optimal":
            # Detect possibilities
            if self.has_kevent():  # kevent
                setup_kevent_poller()
            elif self.has_epoll():
                setup_epoll_poller()  # epoll
            elif self.has_poll():  # poll
                setup_poll_poller()
            else:  # Fallback to select
                setup_select_poller()
        elif polling_method == "kevent" and self.has_kevent():
            setup_kevent_poller()
        elif polling_method == "epoll" and self.has_epoll():
            setup_epoll_poller()
        elif polling_method == "poll" and self.has_poll():
            setup_poll_poller()
        else:
            # Fallback to select
            setup_select_poller()

    def register_socket(self, socket, name=None):
        """
        Register socket to a factory. Socket became a new socket
        """
        logging.debug("register_socket(%s,%s)" % (socket, name))
        with self.register_lock:
            self.new_sockets += [(socket, name)]

    def unregister_socket(self, socket):
        """
        Remove socket from factory
        """
        with self.register_lock:
            logging.debug("unregister_socket(%s)" % socket)
            if socket not in self.socket_name:  # Not in factory yet
                return
            self.sockets.pop(socket.fileno(), None)
            old_name = self.socket_name.pop(socket, None)
            self.name_socket.pop(old_name, None)
            if socket in self.new_sockets:
                self.new_sockets.remove(socket)

    def guarded_socket_call(self, socket, method):
        """
        Wrapper for safe call of socket method. Handles and reports
        socket errors.

        :return: Call status
        :rtype: Bool
        """
        try:
            method()
        except:
            exc = get_socket_error()
            try:
                if exc:
                    socket.on_error(exc)
                else:
                    socket.error("Unhandled exception when calling %s" % str(method))
                    error_report()
                    socket.close()
            except:
                socket.error("Error when handling error condition")
                error_report()
            return False
        return True

    def init_socket(self, socket, name):
        """
        Initialize new socket. Call socket's create_socket() when necessary
        and attach socket to fabric's event loop
        """
        if not socket.socket_is_ready():
            socket.debug("Initializing socket")
            if not self.guarded_socket_call(socket, socket.create_socket):
                return
        if socket.socket is None:
            # Race condition raised. Socket is unregistered since last socket.create_socket call.
            # Silently ignore and exit
            return
        with self.register_lock:
            self.sockets[socket.fileno()] = socket
            if socket in self.socket_name:
                # Socket was registred
                old_name = self.socket_name[socket]
                del self.socket_name[socket]
                if old_name:
                    del self.name_socket[old_name]
            self.socket_name[socket] = name
            if name:
                self.name_socket[name] = socket

    def listen_tcp(self, address, port, socket_class, backlog=100,
                   nconnects=None, **kwargs):
        """Create listening TCP socket"""
        if not issubclass(socket_class, AcceptedTCPSocket):
            raise ValueError("socket_class should be a AcceptedTCPSocket subclass")
        l = ListenTCPSocket(self, address, port, socket_class, backlog,
                            nconnects, **kwargs)
        l.set_name("listen-tcp-%s:%d" % (address, port))
        return l

    def connect_tcp(self, address, port, socket_class):
        """Create ConnectedTCPSocket"""
        if not issubclass(socket_class, ConnectedTCPSocket):
            raise ValueError("socket_class should be a ConnectedTCPSocket subclass")
        return socket_class(self, address, port)

    def get_socket_by_name(self, name):
        """Get socket by registered name"""
        with self.register_lock:
            return self.name_socket[name]

    def get_name_by_socket(self, socket):
        """Get socket name by instance"""
        with self.register_lock:
            return self.socket_name[socket]

    def __len__(self):
        """Returns a number of factory's sockets"""
        with self.register_lock:
            return len(self.sockets)

    def close_stale(self):
        """Detect and close stale sockets"""
        with self.register_lock:
            for s in [s for s in self.sockets.values() if s.is_stale()]:
                logging.debug("Closing stale socket %s" % s)
                s.close()

    def create_pending_sockets(self):
        """Initialize pending sockets"""
        with self.register_lock:
            while self.new_sockets:
                socket, name = self.new_sockets.pop(0)
                self.init_socket(socket, name)

    def loop(self, timeout=1):
        """
        Generic event loop. Depends upon get_active_sockets() method, set
        up by factory constructor
        """
        self.create_pending_sockets()
        if self.sockets:
            r, w = self.get_active_sockets(timeout)
            self.cnt_polls += 1
            #logging.debug("Active sockets: Read=%s Write=%s"%(repr(r), repr(w)))
            # Process write events before read to catch refused connections
            for fd in w:
                s = self.sockets.get(fd)
                if s:
                    self.guarded_socket_call(s, s.handle_write)
            # Process read events
            for fd in r:
                s = self.sockets.get(fd)
                if s:
                    self.guarded_socket_call(s, s.handle_read)
        else:
            # No socket initialized. Sleep to prevent CPU hogging
            time.sleep(timeout)

    ##
    ## Straightforward select() implementation
    ## Returns a list of (read fds, write fds)
    ##
    def get_active_select(self, timeout):
        """
        select() implementation

        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        # Get read and write candidates
        with self.register_lock:
            r = [f for f, s in self.sockets.items() if s.can_read()]
            w = [f for f, s in self.sockets.items() if s.can_write()]
        # Poll socket status
        try:
            r, w, x = select.select(r, w, [], timeout)
            return r, w
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except KeyboardInterrupt:
            logging.info("Got Ctrl+C, exiting")
            sys.exit(0)
        except:
            error_report()
            return [], []

    def get_active_poll(self, timeout):
        """
        poll() implementation

        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        poll = select.poll()
        # Get read and write candidates
        with self.register_lock:
            for f, s in self.sockets.items():
                e = ((select.POLLIN if s.can_read() else 0) |
                     (select.POLLOUT if s.can_write() else 0))
                if e:
                    poll.register(f, e)
        # Poll socket status
        try:
            events = poll.poll(timeout * 1000)  # ms->s
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except:
            return [], []
        # Build result
        rset = [fd for fd, e in events if e & (select.POLLIN | select.POLLHUP)]
        wset = [fd for fd, e in events if e & select.POLLOUT]
        return rset, wset

    def get_active_kevent(self, timeout):
        """
        kevent() implementation. Broken.

        :returns: Tuple of (List of read socket ids, Write socket ids)
        """
        # Get read and write candidates
        kqueue = select.kqueue()
        l = 0
        with self.register_lock:
            for f, s in self.sockets.items():
                if s.can_write():
                    kqueue.control([select.kevent(f, select.KQ_FILTER_WRITE,
                                                  select.KQ_EV_ADD)], 0)
                    l += 1
                if s.can_read():
                    kqueue.control([select.kevent(f, select.KQ_FILTER_READ,
                                                  select.KQ_EV_ADD)], 0)
                    l += 1
        # Poll events
        rset = []
        wset = []
        for e in kqueue.control(None, l, timeout):
            if e.filter & select.KQ_FILTER_WRITE:
                wset += [e.ident]
            if e.filter & select.KQ_FILTER_READ:
                rset += [e.ident]
        return rset, wset

    def get_active_epoll(self, timeout):
        """
        epoll() implementation

        :returns: Tuple of (List of read socket ids, Write socket ids)
        """

        epoll = select.epoll()
        # Get read and write candidates
        with self.register_lock:
            for f, s in self.sockets.items():
                e = ((select.EPOLLIN if s.can_read() else 0) |
                     (select.EPOLLOUT if s.can_write() else 0))
                if e:
                    epoll.register(f, e)
        # Poll socket status
        try:
            events = epoll.poll(timeout)
        except select.error, why:
            if why[0] not in (EINTR, EBADF):
                error_report()  # non-ignorable errors
            return [], []
        except:
            return [], []
        # Build result
        rset = [fd for fd, e in events if e & (select.EPOLLIN | select.EPOLLHUP)]
        wset = [fd for fd, e in events if e & select.EPOLLOUT]
        return rset, wset

    def run(self, run_forever=False):
        """
        Socket factory event loop.

        :param run_forever: Run event loop forever, when True, else shutdown
                            fabric when no sockets available
        """
        logging.debug("Running socket factory")
        self.create_pending_sockets()
        if run_forever:
            cond = lambda: True
        else:
            cond = lambda: len(self.sockets) > 0
            # Wait for any socket
            while not cond():
                time.sleep(1)
        last_tick = last_stale = time.time()
        while cond() and not self.to_shutdown:
            self.loop(1)
            t = time.time()
            if self.tick_callback and t - last_tick >= 1:
                try:
                    self.tick_callback()
                except:
                    error_report()
                    logging.info("Restoring from tick() failure")
                last_tick = t
            if t - last_stale > 3:
                self.close_stale()
                last_stale = t
