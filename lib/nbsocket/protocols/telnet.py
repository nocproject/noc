# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Telnet protocol parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nbsocket.protocols import Protocol

##
## Telnet protocol parser
##
IAC = chr(0xFF)  # Interpret As Command
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
# ECHO+SGA+TTYPE+NAWS
ACCEPTED_TELNET_OPTIONS = set([chr(c) for c in (1, 3, 24, 31)])
IS = "\x00"
SEND = "\x01"


class TelnetProtocol(Protocol):
    def __init__(self, parent, callback):
        super(TelnetProtocol, self).__init__(parent, callback)
        self.iac_seq = ""
        self.sb_seq = None
        self.naws = "\xff\xff\xff\xff"

    def set_options(self, naws=None):
        if naws is not None:
            self.naws = naws

    def write_iac(self, msg):
        self.parent.out_buffer += msg
        self.parent.set_status(w=bool(self.parent.out_buffer) and self.parent.is_connected)

    def iac_response(self, command, opt):
        self.debug("Sending IAC %s" % self.iac_repr(command, opt))
        self.write_iac(IAC + command + opt)

    def sb_response(self, command, opt, data=None):
        sb = IAC + SB + command + opt
        if data:
            sb += data
        sb += IAC + SE
        self.debug("Sending SB %s" % repr(sb))
        self.write_iac(sb)

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
        else:
            return  # Ignore invalid IAC command
        self.iac_response(r, opt)
        # Process NAWS
        if cmd == DO and opt == "\x1f":  # NAWS
            self.sb_response("\x1f", self.naws)

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
