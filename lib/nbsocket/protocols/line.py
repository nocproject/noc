# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Line protocol parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nbsocket.protocols import Protocol


class LineProtocol(Protocol):
    """
    Simple line-based protocols. PDUs are separated by "\n"
    """
    def parse_pdu(self):
        pdus = self.in_buffer.split("\n")
        self.in_buffer = pdus.pop(-1)
        return pdus
