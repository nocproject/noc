# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for Line protocol
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import NOCTestCase
from noc.lib.nbsocket.protocols.line import LineProtocol


class LineTestCase(NOCTestCase):
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
        line = LineProtocol(stub, stub.write)
        for p in packets:
            line.feed(p)
        self.assertEquals(stub.out_buffer, response)

    def test_line(self):
        self.assertResponse(["1\n", "2\n", "3\n"], "123")
        self.assertResponse(["1\n2\n345\n"], "12345")
