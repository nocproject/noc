# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP protocol PDU
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from pdu import stomp_parse_frame
from noc.lib.nbsocket import Protocol


class STOMPProtocol(Protocol):
    """
    STOMP Protocol PDU is a simple zero-terminated string
    """
    def parse_pdu(self):
        # Split PDUs
        r = self.in_buffer.split("\x00")
        if r:
            self.in_buffer = r.pop(-1)
        # Parse PDUs
        # @todo: check header limits
        for pdu in r:
            self.parent.debug("Receiving STOMP frame:\n%s" % pdu)
            try:
                yield stomp_parse_frame(pdu)
            except ValueError, why:
                self.send_error(pdu, str(why))

    def send_error(self, pdu, error):
        """
        Send back ERROR message
        :param pdu:
        :param error:
        :return:
        """
        # Cut headers
        h_start, h_stop = self.find_header(pdu)
        if h_start is None:
            headers = ""
        else:
            headers = pdu[h_start:h_stop]
        i1 = pdu.find("\n")
        if i1 > 0:
            i2 = pdu.find("\n\n", i1 + 1)
            if i2 > 0:
                headers = pdu[i1 + 1:i2]
        # Send ERROR message
        self.parent.write("ERROR\n%s\n\n%s\x00" % (
            headers, error))

    def find_header(self, pdu):
        """
        Return header's start, stop or None, None
        :param pdu:
        :return:
        """
        i1 = pdu.find("\n")
        if i1 > 0:
            i2 = pdu.find("\n\n", i1 + 1)
            if i2 > 0:
                return i1 + 1, i2
        return None, None
