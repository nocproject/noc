# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for Telnet client protocol
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import NOCTestCase
from noc.lib.nbsocket.protocols.telnet import *


class TelnetTestCase(NOCTestCase):
    class SocketStub(object):
        def __init__(self):
            self.out_buffer = ""

        def debug(self, msg):
            pass

        def write(self, s):
            self.out_buffer += s

    def assertResponse(self, packets, response):
        """
        Create telnet protocol instance, feed the input packets
        and collect output
        """
        stub = self.SocketStub()
        telnet = TelnetProtocol(stub, stub.write)
        for p in packets:
            telnet.feed(p)
        self.assertEquals(stub.out_buffer, response)

    def test_plain(self):
        self.assertResponse(["Lorem ipsum"], "Lorem ipsum")
        self.assertResponse(["Lorem ", "ipsum"], "Lorem ipsum")

    def test_doubled_iacs(self):
        self.assertResponse([IAC + IAC + "Lorem ipsum"], IAC + "Lorem ipsum")
        self.assertResponse(["Lorem " + IAC + IAC + "ipsum"],
                            "Lorem " + IAC + "ipsum")
        self.assertResponse(["Lorem ipsum" + IAC + IAC],
                            "Lorem ipsum" + IAC)
        self.assertResponse([IAC, IAC, "Lorem ipsum"],
                            IAC + "Lorem ipsum")
        self.assertResponse([IAC, IAC + "Lorem ipsum"],
                            IAC + "Lorem ipsum")
        self.assertResponse(["Lorem " + IAC, IAC + "ipsum"],
                            "Lorem " + IAC + "ipsum")
        self.assertResponse(["Lorem ", IAC, IAC, "ipsum"],
                            "Lorem " + IAC + "ipsum")
        self.assertResponse(["Lorem ", IAC + IAC, "ipsum"],
                            "Lorem " + IAC + "ipsum")
        self.assertResponse(["Lorem ", IAC +  IAC + "ipsum"],
                            "Lorem " + IAC + "ipsum")
        self.assertResponse(["Lorem ", IAC,  IAC + "ipsum"],
                            "Lorem " + IAC + "ipsum")

    def test_iac(self):
        for cmd in IAC_CMD:
            for opt in TELNET_OPTIONS:
                opt = chr(opt)
                if cmd == DO:
                    r = WILL if opt in ACCEPTED_TELNET_OPTIONS else WONT
                elif cmd == DONT:
                    r = WONT
                elif cmd == WILL:
                    r = DO if opt in ACCEPTED_TELNET_OPTIONS else DONT
                elif cmd == WONT:
                    r = DONT
                sb = ""
                if cmd == DO and opt == "\x1f":
                    # Negotiate NAWS NAWS
                    # IAC SB NAWS FF FF FF FF IAC SE
                    sb = "\xff\xfa\x1f\xff\xff\xff\xff\xff\xf0"
                self.assertResponse([IAC + cmd + opt], IAC + r + opt + sb)
                self.assertResponse([IAC, cmd + opt], IAC + r + opt + sb)
                self.assertResponse([IAC + cmd, opt], IAC + r + opt + sb)
                self.assertResponse([IAC, cmd, opt], IAC + r + opt + sb)

    def test_sb(self):
        TTYPE = "\x18"
        self.assertResponse(["Unknown " + IAC + SB + "xx" + IAC + SE + "SB"],
                            "Unknown SB")
        self.assertResponse([IAC + SB + TTYPE + SEND + IAC + SE],
                            IAC + SB + TTYPE + IS + "XTERM" + IAC + SE)
