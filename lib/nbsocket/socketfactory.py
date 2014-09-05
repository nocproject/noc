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
import time
from threading import RLock
## NOC modules
from noc.lib.debug import error_report
from exceptions import get_socket_error
from listentcpsocket import ListenTCPSocket
from connectedtcpsocket import ConnectedTCPSocket
from acceptedtcpsocket import AcceptedTCPSocket
from pollers.detect import get_poller
from pipesocket import PipeSocket

logger = logging.getLogger(__name__)


class SocketFactory(object):
    """
    Socket factory is a major event loop controller, maintaining full socket
    lifetime
    """
    def __init__(self, tick_callback=None,
                 polling_method=None, controller=None,
                 write_delay=True):
        self.sockets = {}      # fileno -> socket
        self.socket_name = {}  # socket -> name
        self.name_socket = {}  # name -> socket
        self.new_sockets = []  # list of (socket,name)
        self.tick_callback = tick_callback
        self.to_shutdown = False
        self.register_lock = RLock()  # Guard for register/unregister operations
        self.controller = controller  # Reference to controlling daemon
        if polling_method is None:
            # Read settings if available
            try:
                from noc.settings import config
                polling_method = config.get("main", "polling_method")
            except ImportError:
                polling_method = "select"
        self.poller = get_poller(polling_method)
        # Performance data
        self.cnt_polls = 0  # Number of polls
        self.write_delay = write_delay
        if not self.write_delay:
            self.control = PipeSocket(self)

    def shutdown(self):
        """
        Shut down socket factory and exit next event loop
        """
        logger.info("Shutting down the factory")
        self.to_shutdown = True

    def register_socket(self, socket, name=None):
        """
        Register socket to a factory. Socket became a new socket
        """
        logger.debug("Register socket %s (%s)", socket, name)
        with self.register_lock:
            self.new_sockets += [(socket, name)]

    def unregister_socket(self, socket):
        """
        Remove socket from factory
        """
        with self.register_lock:
            logger.debug("Unregister socket %s", socket)
            self.set_status(socket, r=False, w=False)
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
        except Exception:
            exc = get_socket_error()
            try:
                if exc:
                    socket.on_error(exc)
                else:
                    socket.error("Unhandled exception when calling %s" % str(method))
                    error_report()
                    socket.close()
            except Exception:
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
        if not socket.socket_is_ready():
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
                logger.debug("Closing stale socket %s", s)
                s.stale = True
                s.close()

    def create_pending_sockets(self):
        """Initialize pending sockets"""
        with self.register_lock:
            while self.new_sockets:
                socket, name = self.new_sockets.pop(0)
                self.init_socket(socket, name)

    def set_status(self, sock, r=None, w=None):
        with self.register_lock:
            if r is not None:
                if r:
                    self.poller.add_reader(sock)
                else:
                    self.poller.remove_reader(sock)
            if w is not None:
                if w:
                    self.poller.add_writer(sock)
                    if not self.write_delay:
                        # Force get_active() completion
                        self.control.write("x")
                else:
                    self.poller.remove_writer(sock)

    def loop(self, timeout=1):
        """
        Generic event loop
        """
        self.create_pending_sockets()
        if self.sockets:
            r, w = self.poller.get_active(timeout)
            self.cnt_polls += 1
            # Process write events before read
            # to catch refused connections
            for s in w:
                self.guarded_socket_call(s, s.handle_write)
            # Process read events
            for s in r:
                self.guarded_socket_call(s, s.handle_read)
        else:
            # No socket initialized. Sleep to prevent CPU hogging
            time.sleep(timeout)

    def run(self, run_forever=False):
        """
        Socket factory event loop.

        :param run_forever: Run event loop forever, when True, else shutdown
                            fabric when no sockets available
        """
        logger.info("Running socket factory (%s)", self.poller.__class__.__name__)
        self.create_pending_sockets()
        if run_forever:
            cond = lambda: True
        else:
            if self.write_delay:
                cond = lambda: bool(self.sockets)
            else:
                cond = lambda: len(self.sockets) > 1
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
                except Exception:
                    error_report()
                    logger.info("Restoring from tick() failure")
                last_tick = t
            if t - last_stale >= 1:
                self.close_stale()
                last_stale = t
        logger.info("Stopping socket factory")
