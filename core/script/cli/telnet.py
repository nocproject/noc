# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Telnet CLI
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Tornado modules
from tornado.iostream import IOStream
## NOC modules
from base import CLI

IAC = chr(0xFF)  # Interpret As Command
DONT = chr(0xFE)
DO = chr(0xFD)
WONT = chr(0xFC)
WILL = chr(0xFB)
SB = chr(0xFA)
SE = chr(0xF0)
NAWS = chr(0x1F)

IAC_CMD = {
    DO: "DO",
    DONT: "DONT",
    WILL: "WILL",
    WONT: "WONT"
}

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
ACCEPTED_TELNET_OPTIONS = "\x01\x03\x18\x1f"


class TelnetIOStream(IOStream):
    def __init__(self, sock, cli):
        super(TelnetIOStream, self).__init__(sock)
        self.cli = cli
        self.logger = cli.logger
        self.iac_seq = ""
        self.naws = "\x00\x80\x00\x80"

    def read_from_fd(self):
        chunk = super(TelnetIOStream, self).read_from_fd()
        if self.iac_seq:
            # Restore incomplete IAC context
            chunk = self.iac_seq + chunk
            self.iac_seq = ""
        r = []
        while chunk:
            left, seq, right = chunk.partition(IAC)
            r += [left]
            if seq:
                # Process IAC sequence
                if not right or len(right) == 1:
                    # Incomplete sequence
                    # Collect for next round
                    self.iac_seq = IAC + right
                    break
                elif right[0] == IAC:
                    # <IAC> <IAC> leads to single <IAC>
                    r += [IAC]
                    chunk = right[1:]
                elif right[0] != SB:
                    # Process IAC <cmd> <opt>
                    self.process_iac(right[0], right[1])
                    chunk = right[2:]
                else:
                    # Process IAC SB ... SE sequence
                    pass
            else:
                # Return leftovers
                break
        return "".join(r)

    def write(self, data, callback=None):
        data = data.replace(IAC, IAC + IAC)
        return super(TelnetIOStream, self).write(data,
                                                 callback=callback)

    def send_iac(self, cmd, opt):
        """
        Send IAC response
        """
        def cb(*args, **kwargs):
            pass

        self.logger.debug("Send %s", self.iac_repr(cmd, opt))
        self.write_to_fd(IAC + cmd + opt)

    def send_iac_sb(self, opt, data=None):
        sb = IAC + SB + opt
        if data:
            sb += data
        sb += IAC + SE
        self.logger.debug("Send IAC SB %r %r IAC SE",
                          opt, data)
        self.write_to_fd(sb)

    def process_iac(self, cmd, opt):
        """
        Process IAC command.
        """
        self.logger.debug("Received %s", self.iac_repr(cmd, opt))
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
        self.send_iac(r, opt)
        # Send NAWS response
        if cmd == DO and opt == NAWS:
            self.send_iac_sb(opt, self.naws)

    def iac_repr(self, cmd, opt):
        """
        Human-readable IAC sequence
        :param cmd:
        :param opt:
        :return:
        """
        if isinstance(opt, basestring):
            opt = ord(opt)
        return "%s %s" % (
            IAC_CMD.get(cmd, cmd),
            TELNET_OPTIONS.get(opt, opt),
        )

class TelnetCLI(CLI):
    name = "telnet"
    default_port = 23
    iostream_class = TelnetIOStream
