# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pymongo pool
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import threading
# Third-party modules
from pymongo import thread_util
from pymongo.pool import Pool as BasePool
from pymongo.network import SocketChecker


class Pool(BasePool):
    def __init__(self, address, options, handshake=True):
        """
        :Parameters:
          - `address`: a (hostname, port) tuple
          - `options`: a PoolOptions instance
          - `handshake`: whether to call ismaster for each new SocketInfo
        """
        # Check a socket's health with socket_closed() every once in a while.
        # Can override for testing: 0 to always check, None to never check.
        self._check_interval_seconds = 1

        self.sockets = []
        self.lock = threading.Lock()
        self.active_sockets = 0

        # Keep track of resets, so we notice sockets created before the most
        # recent reset and close them.
        self.pool_id = 0
        self.pid = os.getpid()
        self.address = address
        self.opts = options
        self.handshake = handshake

        if (self.opts.wait_queue_multiple is None or
                self.opts.max_pool_size is None):
            max_waiters = None
        else:
            max_waiters = self.opts.max_pool_size * self.opts.wait_queue_multiple

        self._socket_semaphore = thread_util.create_semaphore(
            self.opts.max_pool_size, max_waiters)
        self.socket_checker = SocketChecker()

    def reset(self):
        with self.lock:
            self.pool_id += 1
            self.pid = os.getpid()
            sockets, self.sockets = self.sockets, []
            self.active_sockets = 0

        for sock_info in sockets:
            sock_info.close()

    def remove_stale_sockets(self):
        """
        Removes stale sockets then adds new ones if pool is too small.
        """
        if self.opts.max_idle_time_seconds is not None:
            with self.lock:
                while (self.sockets and
                       self.sockets[-1].idle_time_seconds() > self.opts.max_idle_time_seconds):
                    sock_info = self.sockets.pop(-1)
                    sock_info.close()

        while True:
            with self.lock:
                if (len(self.sockets) + self.active_sockets >=
                        self.opts.min_pool_size):
                    # There are enough sockets in the pool.
                    break

            # We must acquire the semaphore to respect max_pool_size.
            if not self._socket_semaphore.acquire(False):
                break
            try:
                sock_info = self.connect()
                with self.lock:
                    self.sockets.insert(0, sock_info)
            finally:
                self._socket_semaphore.release()

    def _get_socket_no_auth(self):
        """Get or create a SocketInfo. Can raise ConnectionFailure."""
        # We use the pid here to avoid issues with fork / multiprocessing.
        # See test.test_client:TestClient.test_fork for an example of
        # what could go wrong otherwise
        if self.pid != os.getpid():
            self.reset()
        # Get a free socket or create one.
        if not self._socket_semaphore.acquire(
                True, self.opts.wait_queue_timeout):
            self._raise_wait_queue_timeout()
        with self.lock:
            self.active_sockets += 1

        # We've now acquired the semaphore and must release it on error.
        try:
            try:
                # set.pop() isn't atomic in Jython less than 2.7, see
                # http://bugs.jython.org/issue1854
                with self.lock:
                    # Can raise ConnectionFailure.
                    sock_info = self.sockets.pop(0)
            except IndexError:
                # Can raise ConnectionFailure or CertificateError.
                sock_info = self.connect()
            else:
                # Can raise ConnectionFailure.
                sock_info = self._check(sock_info)
        except Exception:
            self._socket_semaphore.release()
            with self.lock:
                self.active_sockets -= 1
            raise

        return sock_info

    def return_socket(self, sock_info):
        """Return the socket to the pool, or if it's closed discard it."""
        if self.pid != os.getpid():
            self.reset()
        else:
            if sock_info.pool_id != self.pool_id:
                sock_info.close()
            elif not sock_info.closed:
                sock_info.update_last_checkin_time()
                with self.lock:
                    self.sockets.insert(0, sock_info)

        self._socket_semaphore.release()
        with self.lock:
            self.active_sockets -= 1
