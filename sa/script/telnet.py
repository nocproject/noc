# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Telnet provider
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket
from noc.lib.nbsocket.protocols.telnet import *
from noc.sa.script.cli import CLI

D_IAC = IAC + IAC  # Doubled IAC


class CLITelnetSocket(CLI, ConnectedTCPSocket):
    """
    Telnet client
    """
    TTL = 30
    protocol_class = TelnetProtocol

    def __init__(self, script):
        self.script = script
        self._log_label = "TELNET: %s" % self.script.access_profile.address
        CLI.__init__(self, self.script.profile, self.script.access_profile)
        ConnectedTCPSocket.__init__(self, self.script.activator.factory,
                                    self.script.access_profile.address,
                                    self.script.access_profile.port or 23)
        self.protocol.set_options(naws=self.script.profile.telnet_naws)

    def write(self, s):
        if type(s) == unicode:
            if self.script.encoding:
                s = s.encode(self.script.encoding)
            else:
                s = str(s)
        # Double all IACs
        super(CLITelnetSocket, self).write(s.replace(IAC, D_IAC))

    def is_stale(self):
        self.async_check_fsm()
        return ConnectedTCPSocket.is_stale(self)

    def log_label(self):
        return self._log_label

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.log_label(), msg))

    def on_close(self):
        state = self.get_state()
        if state == "SSH_START":
            self.motd = "Connection timeout"
            self.set_state("FAILURE")
        elif self.stale:
            self.queue.put(None)  # Signal stale socket timeout

    def on_conn_refused(self):
        self.debug("Connection refused")
        self.motd = "Connection refused"
        self.set_state("FAILURE")

    def on_connect(self):
        super(CLITelnetSocket, self).on_connect()
        r = self.script.profile.telnet_send_on_connect
        if r is not None:
            self.debug("Sending %s on connect" % repr(r))
            self.write(r)

    def on_PASSWORD_enter(self):
        if self.script.profile.telnet_slow_send_password:
            self.set_character_mode(True)
        super(CLITelnetSocket, self).on_PASSWORD_enter()

    def on_PASSWORD_exit(self):
        if self.script.profile.telnet_slow_send_password:
            self.set_character_mode(False)
