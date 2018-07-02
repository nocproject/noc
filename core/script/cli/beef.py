# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BeefCLI
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import socket
# Third-party modules
import tornado.gen
from tornado.concurrent import TracebackFuture
# NOC modules
from .base import CLI
from .telnet import TelnetIOStream


class BeefCLI(CLI):
    name = "beef_cli"
    default_port = 23

    def create_iostream(self):
        self.state = "notconnected"
        self.sender, receiver = socket.socketpair()
        return BeefIOStream(receiver, self)

    @tornado.gen.coroutine
    def send(self, cmd):
        # @todo: Apply encoding
        cmd = str(cmd)
        self.logger.debug("Send: %r", cmd)
        if self.state != "prompt":
            raise tornado.gen.Return()  # Will be replied via reply_state
        beef = self.script.request_beef()
        try:
            for reply in beef.iter_cli_reply(cmd[:-len(self.profile.command_submit)]):
                self.sender.send(reply)
                yield
        except KeyError:
            # Propagate exception
            self.sender.send(self.SYNTAX_ERROR_CODE)
            yield

    def set_state(self, state):
        changed = self.state != state
        super(BeefCLI, self).set_state(state)
        # Force state enter reply
        if changed:
            self.ioloop.add_callback(self.reply_state, state)

    @tornado.gen.coroutine
    def reply_state(self, state):
        """
        Spool state entry sequence
        :param state:
        :return:
        """
        self.logger.debug("Replying '%s' state", state)
        beef = self.script.request_beef()
        for reply in beef.iter_fsm_state_reply(state):
            self.sender.send(reply)
            yield

    def close(self):
        self.sender.close()
        self.sender = None
        super(BeefCLI, self).close()


class BeefIOStream(TelnetIOStream):
    def connect(self, *args, **kwargs):
        """
        Always connected
        :param args:
        :param kwargs:
        :return:
        """
        future = self._connect_future = TracebackFuture()
        # Force beef downloading
        beef = self.cli.script.request_beef()
        if not beef:
            # Connection refused
            self.close(exc_info=True)
            return future
        future.set_result(True)
        # Start replying start state
        self.cli.set_state("start")
        self._add_io_state(self.io_loop.WRITE)
        return future

    def close(self):
        self.socket.close()
        self.socket = None
