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
from noc.lib.nbsocket import ConnectedTCPSocket, Protocol
from noc.sa.script.cli import CLI

##
## Telnet protocol parser
##
IAC = chr(0xFF)  # Interpret As Command
D_IAC = IAC + IAC  # Doubled IAC
DONT = chr(0xFE)
DO = chr(0xFD)
WONT = chr(0xFC)
WILL = chr(0xFB)
SB = chr(0xFA)
SE = chr(0xF0)
IAC_CMD = (DO, DONT, WONT, WILL)
TELNET_OPTIONS = {
    0: "BINARY",
    1: "ECHO",
    2: "RCP",
    3: "SGA",
    4: "NAMS",
    5: "STATUS",
    6: "TM",
    7: "RCTE",
    8: "NAOL",
    9: "NAOP",
    10: "NAOCRD",
    11: "NAOHTS",
    12: "NAOHTD",
    13: "NAOFFD",
    14: "NAOVTS",
    15: "NAOVTD",
    16: "NAOLFD",
    17: "XASCII",
    18: "LOGOUT",
    19: "BM",
    20: "DET",
    21: "SUPDUP",
    22: "SUPDUPOUTPUT",
    23: "SNDLOC",
    24: "TTYPE",
    25: "EOR",
    26: "TUID",
    27: "OUTMRK",
    28: "TTYLOC",
    29: "3270REGIME",
    30: "X3PAD",
    31: "NAWS",
    32: "TSPEED",
    33: "LFLOW",
    34: "LINEMODE",
    35: "XDISPLOC",
    36: "OLD_ENVIRON",
    37: "AUTHENTICATION",
    38: "ENCRYPT",
    39: "NEW_ENVIRON",
    255: "EXOPL",
}

ACCEPTED_TELNET_OPTIONS = set([chr(c) for c in (1, 3, 24)])  # ECHO+SGA+TTYPE
IS = "\x00"
SEND = "\x01"


class TelnetProtocol(Protocol):
    def __init__(self, parent, callback):
        super(TelnetProtocol, self).__init__(parent, callback)
        self.iac_seq = ""
        self.sb_seq = None

    def iac_response(self, command, opt):
        self.debug("Sending IAC %s" % self.iac_repr(command, opt))
        self.parent.out_buffer += IAC + command + opt

    def sb_response(self, command, opt, data=None):
        sb = IAC + SB + command + opt
        if data:
            sb += data
        sb += IAC + SE
        self.debug("Sending SB %s" % repr(sb))
        self.parent.out_buffer += sb

    def process_sb(self, sb):
        self.debug("Received SB %s" % repr(sb))
        if sb == "\x18\x01":  # TTYPE SEND
            self.sb_response("\x18", "\x00", "XTERM")  # TTYPE IS XTERM

    def process_iac(self, cmd, opt):
        self.debug("Received IAC %s" % self.iac_repr(cmd, opt))
        if cmd == DO:
            r = WILL if opt in ACCEPTED_TELNET_OPTIONS else WONT
        elif cmd == DONT:
            r = WONT
        elif cmd == WILL:
            r = DO if opt in ACCEPTED_TELNET_OPTIONS else DONT
        elif cmd == WONT:
            r = DONT
        self.iac_response(r, opt)

    def parse_pdu(self):
        def tc(s):
            return s.replace("\000", "").replace("\021", "")

        while self.in_buffer:
            if self.sb_seq is not None:  # Continue SB sequence processing
                left, seq, self.in_buffer = self.in_buffer.partition(IAC + SE)
                self.sb_seq += left
                if seq:
                    self.process_sb(self.sb_seq)
                    self.sb_seq = None
            elif self.iac_seq == IAC:  # Parse IAC command
                cmd = self.in_buffer[0]
                self.in_buffer = self.in_buffer[1:]
                if cmd == IAC:
                    yield IAC
                    self.iac_seq = ""
                elif cmd == SB:
                    self.sb_seq = ""
                    self.iac_seq = ""
                else:
                    self.iac_seq += cmd
            elif self.iac_seq:
                opt = self.in_buffer[0]
                self.in_buffer = self.in_buffer[1:]
                self.process_iac(self.iac_seq[1], opt)
                self.iac_seq = ""
            else:  # No IAC/SB context
                left, seq, self.in_buffer = self.in_buffer.partition(IAC)
                if seq:  # IAC found
                    if left:
                        yield tc(left)  # Yield all before IAC
                    self.iac_seq = IAC
                else:
                    yield tc(left)  # No IAC found, yield and break

    def iac_repr(self, cmd, opt):
        """
        Human-readable IAC sequence
        :param cmd:
        :param opt:
        :return:
        """
        if isinstance(opt, basestring):
            opt = ord(opt)
        return "%s %s (%s %s)" % (
            {DO: "DO",
             DONT: "DONT",
             WILL: "WILL",
             WONT: "WONT"}.get(cmd, "???"),
            TELNET_OPTIONS.get(opt, "???"),
            ord(cmd),
            opt)

    def debug(self, msg):
        self.parent.debug(msg)


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
        if self.get_state() == "START":
            self.motd = "Connection timeout"
            self.set_state("FAILURE")

    def on_connect(self):
        super(CLITelnetSocket, self).on_connect()
        r = self.script.profile.telnet_send_on_connect
        if r is not None:
            self.debug("Sending %s on connect" % repr(r))
            self.write(r)
