# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# MML class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import socket
import datetime
import re
# Third-party modules
import tornado.ioloop
import tornado.iostream
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.log import PrefixLoggerAdapter
from .error import MMLConnectionRefused, MMLAuthFailed, MMLBadResponse, MMLError
from noc.core.span import Span


class MMLBase(object):
    name = "mml"
    iostream_class = None
    default_port = None
    BUFFER_SIZE = config.activator.buffer_size
    MATCH_TAIL = 256
    # Retries on immediate disconnect
    CONNECT_RETRIES = config.activator.connect_retries
    # Timeout after immediate disconnect
    CONNECT_TIMEOUT = config.activator.connect_timeout
    # compiled capabilities
    HAS_TCP_KEEPALIVE = hasattr(socket, "SO_KEEPALIVE")
    HAS_TCP_KEEPIDLE = hasattr(socket, "TCP_KEEPIDLE")
    HAS_TCP_KEEPINTVL = hasattr(socket, "TCP_KEEPINTVL")
    HAS_TCP_KEEPCNT = hasattr(socket, "TCP_KEEPCNT")
    HAS_TCP_NODELAY = hasattr(socket, "TCP_NODELAY")
    # Time until sending first keepalive probe
    KEEP_IDLE = 10
    # Keepalive packets interval
    KEEP_INTVL = 10
    # Terminate connection after N keepalive failures
    KEEP_CNT = 3

    def __init__(self, script, tos=None):
        self.script = script
        self.profile = script.profile
        self.logger = PrefixLoggerAdapter(self.script.logger, self.name)
        self.iostream = None
        self.ioloop = None
        self.command = None
        self.buffer = ""
        self.is_started = False
        self.result = None
        self.error = None
        self.is_closed = False
        self.close_timeout = None
        self.current_timeout = None
        self.tos = tos
        self.rx_mml_end = re.compile(self.script.profile.pattern_mml_end, re.MULTILINE)
        if self.script.profile.pattern_mml_continue:
            self.rx_mml_continue = re.compile(self.script.profile.pattern_mml_continue, re.MULTILINE)
        else:
            self.rx_mml_continue = None

    def close(self):
        self.script.close_current_session()
        self.close_iostream()
        if self.ioloop:
            self.logger.debug("Closing IOLoop")
            self.ioloop.close(all_fds=True)
            self.ioloop = None
        self.is_closed = True

    def close_iostream(self):
        if self.iostream:
            self.iostream.close()

    def deferred_close(self, session_timeout):
        if self.is_closed or not self.iostream:
            return
        self.logger.debug("Setting close timeout to %ss",
                          session_timeout)
        # Cannot call call_later directly due to
        # thread-safety problems
        # See tornado issue #1773
        tornado.ioloop.IOLoop.instance().add_callback(
            self._set_close_timeout,
            session_timeout
        )

    def _set_close_timeout(self, session_timeout):
        """
        Wrapper to deal with IOLoop.add_timeout thread safety problem
        :param session_timeout:
        :return:
        """
        self.close_timeout = tornado.ioloop.IOLoop.instance().call_later(
            session_timeout,
            self.close
        )

    def create_iostream(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.tos:
            s.setsockopt(
                socket.IPPROTO_IP, socket.IP_TOS, self.tos
            )
        if self.HAS_TCP_NODELAY:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self.HAS_TCP_KEEPALIVE:
            s.setsockopt(
                socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1
            )
            if self.HAS_TCP_KEEPIDLE:
                s.setsockopt(socket.SOL_TCP,
                             socket.TCP_KEEPIDLE, self.KEEP_IDLE)
            if self.HAS_TCP_KEEPINTVL:
                s.setsockopt(socket.SOL_TCP,
                             socket.TCP_KEEPINTVL, self.KEEP_INTVL)
            if self.HAS_TCP_KEEPCNT:
                s.setsockopt(socket.SOL_TCP,
                             socket.TCP_KEEPCNT, self.KEEP_CNT)
        return self.iostream_class(s, self)

    def set_timeout(self, timeout):
        if timeout:
            self.logger.debug("Setting timeout: %ss", timeout)
            self.current_timeout = datetime.timedelta(seconds=timeout)
        else:
            if self.current_timeout:
                self.logger.debug("Resetting timeouts")
            self.current_timeout = None

    def set_script(self, script):
        self.script = script
        if self.close_timeout:
            tornado.ioloop.IOLoop.instance().remove_timeout(self.close_timeout)
            self.close_timeout = None

    @tornado.gen.coroutine
    def send(self, cmd):
        # @todo: Apply encoding
        cmd = str(cmd)
        self.logger.debug("Send: %r", cmd)
        yield self.iostream.write(cmd)

    @tornado.gen.coroutine
    def submit(self):
        # Create iostream and connect, when necessary
        if not self.iostream:
            self.iostream = self.create_iostream()
            address = (
                self.script.credentials.get("address"),
                self.script.credentials.get("cli_port", self.default_port)
            )
            self.logger.debug("Connecting %s", address)
            try:
                yield self.iostream.connect(address)
            except tornado.iostream.StreamClosedError:
                self.logger.debug("Connection refused")
                self.error = MMLConnectionRefused("Connection refused")
                raise tornado.gen.Return(None)
            self.logger.debug("Connected")
            yield self.iostream.startup()
        # Perform all necessary login procedures
        if not self.is_started:
            self.is_started = True
            yield self.send(self.profile.get_mml_login(self.script))
            yield self.get_mml_response()
            if self.error:
                self.error = MMLAuthFailed(str(self.error))
                raise tornado.gen.Return(None)
        # Send command
        yield self.send(self.command)
        r = yield self.get_mml_response()
        raise tornado.gen.Return(r)

    @tornado.gen.coroutine
    def get_mml_response(self):
        result = []
        header_sep = self.profile.mml_header_separator
        while True:
            r = yield self.read_until_end()
            r = r.strip()
            # Process header
            if header_sep not in r:
                self.result = ""
                self.error = MMLBadResponse("Missed header separator")
                raise tornado.gen.Return(None)
            header, r = r.split(header_sep, 1)
            code, msg = self.profile.parse_mml_header(header)
            if code:
                # MML Error
                self.result = ""
                self.error = MMLError("%s (code=%s)" % (msg, code))
                raise tornado.gen.Return(None)
            # Process continuation
            if self.rx_mml_continue:
                # Process continued block
                offset = max(0, len(r) - self.MATCH_TAIL)
                match = self.rx_mml_continue.search(r, offset)
                if match:
                    self.logger.debug("Continuing in the next block")
                    result += [r[:match.start()]]
                    continue
            result += [r]
            break
        self.result = "".join(result)
        raise tornado.gen.Return(self.result)

    def execute(self, cmd, **kwargs):
        """
        Perform command and return result
        :param cmd:
        :param kwargs:
        :return:
        """
        if self.close_timeout:
            self.logger.debug("Removing close timeout")
            self.ioloop.remove_timeout(self.close_timeout)
            self.close_timeout = None
        self.buffer = ""
        self.command = self.profile.get_mml_command(cmd, **kwargs)
        self.error = None
        if not self.ioloop:
            self.logger.debug("Creating IOLoop")
            self.ioloop = tornado.ioloop.IOLoop()
        with Span(server=self.script.credentials.get("address"),
                  service=self.name, in_label=self.command) as s:
            self.ioloop.run_sync(self.submit)
            if self.error:
                if s:
                    s.error_text = str(self.error)
                raise self.error
            else:
                return self.result

    @tornado.gen.coroutine
    def read_until_end(self):
        connect_retries = self.CONNECT_RETRIES
        while True:
            try:
                f = self.iostream.read_bytes(self.BUFFER_SIZE,
                                             partial=True)
                if self.current_timeout:
                    r = yield tornado.gen.with_timeout(
                        self.current_timeout,
                        f
                    )
                else:
                    r = yield f
            except tornado.iostream.StreamClosedError:
                # Check if remote end closes connection just
                # after connection established
                if not self.is_started and connect_retries:
                    self.logger.info(
                        "Connection reset. %d retries left. Waiting %d seconds",
                        connect_retries, self.CONNECT_TIMEOUT
                    )
                    while connect_retries:
                        yield tornado.gen.sleep(self.CONNECT_TIMEOUT)
                        connect_retries -= 1
                        self.iostream = self.create_iostream()
                        address = (
                            self.script.credentials.get("address"),
                            self.script.credentials.get("cli_port", self.default_port)
                        )
                        self.logger.debug("Connecting %s", address)
                        try:
                            yield self.iostream.connect(address)
                            break
                        except tornado.iostream.StreamClosedError:
                            if not connect_retries:
                                raise tornado.iostream.StreamClosedError()
                    continue
                else:
                    raise tornado.iostream.StreamClosedError()
            except tornado.gen.TimeoutError:
                self.logger.info("Timeout error")
                raise tornado.gen.TimeoutError("Timeout")
            self.logger.debug("Received: %r", r)
            self.buffer += r
            offset = max(0, len(self.buffer) - self.MATCH_TAIL)
            match = self.rx_mml_end.search(self.buffer, offset)
            if match:
                self.logger.debug("End of the block")
                r = self.buffer[:match.start()]
                self.buffer = self.buffer[match.end()]
                raise tornado.gen.Return(r)

    def shutdown_session(self):
        if self.profile.shutdown_session:
            self.logger.debug("Shutdown session")
            self.profile.shutdown_session(self.script)
