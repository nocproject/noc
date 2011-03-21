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
IAC=chr(255)  # Interpret As Command
D_IAC=IAC+IAC # Doubled IAC
DONT = chr(254)
DO   = chr(253)
WONT = chr(252)
WILL = chr(251)
IAC_CMD= (DO, DONT, WONT, WILL)
TELNET_OPTIONS={
    0   : "BINARY",
    1   : "ECHO",
    2   : "RCP",
    3   : "SGA",
    4   : "NAMS",
    5   : "STATUS",
    6   : "TM",
    7   : "RCTE",
    8   : "NAOL",
    9   : "NAOP",
    10  : "NAOCRD",
    11  : "NAOHTS",
    12  : "NAOHTD",
    13  : "NAOFFD",
    14  : "NAOVTS",
    15  : "NAOVTD",
    16  : "NAOLFD",
    17  : "XASCII",
    18  : "LOGOUT",
    19  : "BM",
    20  : "DET",
    21  : "SUPDUP",
    22  : "SUPDUPOUTPUT",
    23  : "SNDLOC",
    24  : "TTYPE",
    25  : "EOR",
    26  : "TUID",
    27  : "OUTMRK",
    28  : "TTYLOC",
    29  : "3270REGIME",
    30  : "X3PAD",
    31  : "NAWS",
    32  : "TSPEED",
    33  : "LFLOW",
    34  : "LINEMODE",
    35  : "XDISPLOC",
    36  : "OLD_ENVIRON",
    37  : "AUTHENTICATION",
    38  : "ENCRYPT",
    39  : "NEW_ENVIRON",
    255 : "EXOPL",
}

ACCEPTED_TELNET_OPTIONS=set([chr(c) for c in (1, 3)]) # ECHO+SGA

class TelnetProtocol(Protocol):
    def __init__(self, parent, callback):
        super(TelnetProtocol, self).__init__(parent, callback)
        self.iac_seq=""
    
    def parse_pdu(self):
        while self.in_buffer:
            if not self.iac_seq:
                idx=self.in_buffer.find(IAC)
                if idx==-1:
                    # No IACs in the stream
                    r=self.in_buffer.replace("\000", "").replace("\021", "")
                    self.in_buffer=""
                    yield r
                    continue
                elif idx==0:
                    # IAC is the first character in the stream
                    self.iac_seq=IAC
                    self.in_buffer=self.in_buffer[1:]
                    continue
                else:
                    r=self.in_buffer[:idx].replace("\000", "").replace("\021", "")
                    self.in_buffer=self.in_buffer[idx+1:]
                    self.iac_seq=IAC
                    yield r
                    continue
            else:
                # Process IACs
                if self.iac_seq==IAC:
                    c=self.in_buffer[0]
                    if c in IAC_CMD:
                        self.iac_seq+=c
                        self.in_buffer=self.in_buffer[1:]
                        continue
                    self.iac_seq=""
                    if c==IAC:
                        # Doubled IAC
                        self.in_buffer=self.in_buffer[1:]
                        yield IAC
                        continue
                else:
                    cmd=self.iac_seq[1]
                    opt=self.in_buffer[0]
                    self.iac_seq=""
                    self.in_buffer=self.in_buffer[1:] # Strip option
                    self.debug("Received IAC %s"%self.iac_repr(cmd, opt))
                    # Refuse options
                    iac_response=None
                    if cmd in (DO, DONT):
                        if cmd==DO and opt in ACCEPTED_TELNET_OPTIONS:
                            iac_response=(WILL, opt)
                        else:
                            iac_response=(WONT, opt)
                    elif cmd in (WILL, WONT):
                        if cmd==WILL and opt in ACCEPTED_TELNET_OPTIONS:
                            iac_response=(DO, opt)
                        else:
                            iac_response=(DONT, opt)
                    self.debug("Sending IAC %s"%self.iac_repr(iac_response[0], iac_response[1]))
                    self.parent.out_buffer += IAC+iac_response[0]+iac_response[1]
    
    ##
    ## Human-readable IAC sequence
    ##
    def iac_repr(self, cmd, opt):
        if isinstance(opt, basestring):
            opt=ord(opt)
        return "%s %s (%s %s)"%({DO: "DO", DONT: "DONT", WILL: "WILL", WONT: "WONT"}.get(cmd, "???"),
            TELNET_OPTIONS.get(opt, "???"), ord(cmd), opt)
    
    def debug(self, msg):
        self.parent.debug(msg)

##
## Telnet client
##
class CLITelnetSocket(CLI, ConnectedTCPSocket):
    TTL=30
    protocol_class=TelnetProtocol
    
    def __init__(self, factory, profile, access_profile):
        self._log_label="TELNET: %s"%access_profile.address
        CLI.__init__(self, profile, access_profile)
        port=access_profile.port or 23
        ConnectedTCPSocket.__init__(self, factory, access_profile.address, port)
    
    def write(self, s):
        # Double all IACs
        super(CLITelnetSocket, self).write(str(s).replace(IAC, D_IAC))
    
    def is_stale(self):
        self.async_check_fsm()
        return ConnectedTCPSocket.is_stale(self)
    
    ##
    def log_label(self):
        return self._log_label
    
    ##
    ##
    ##
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.log_label(),msg))
    

