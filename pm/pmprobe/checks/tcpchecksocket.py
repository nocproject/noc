# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TCPCheckSocket
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import re
## NOC modules
from noc.lib.nbsocket.connectedtcpsocket import ConnectedTCPSocket


class TCPCheckSocket(ConnectedTCPSocket):
    def __init__(self, check, address, port=None, timeout=10,
                 request=None, match_response=None, wait_close=False):
        self.check = check
        self.request = request
        if isinstance(match_response, basestring):
            self.match_response = re.compile(match_response)
        else:
            self.match_response = match_response
        self.wait_close = wait_close
        self.response_matched = False
        # Timers
        self.start_time = time.time()
        self.connected_time = None  # 3way handshake completed
        self.response_start = None  # Time of receiving
                                    # first packet of response
        self.response_completed = None  # End time
        #
        self.data = ""
        super(TCPCheckSocket, self).__init__(
            check.get_factory(), address, port)
        self.set_timeout(timeout)

    def on_connect(self):
        self.connected_time = time.time()
        request = self.get_request()
        if request:
            # Send request
            self.write(request)
        elif not self.match_response:
            # No more checks
            self.close()

    def on_conn_refused(self):
        self.info("Connection refused")

    def on_read(self, data):
        if not self.response_start:
            self.response_start = time.time()
        self.data += data
        if self.match_response and not self.response_matched:
            if self.match_response.search(self.data):
                self.response_matched = True
                if not self.wait_close:
                    self.close()

    def on_close(self):
        r = {"result": False}
        if self.connected_time:
            # Check result
            if self.match_response:
                r["result"] = self.response_matched
            else:
                r["result"] = True
            r["connect_delay"] = self.connected_time - self.start_time
            if self.response_start:
                r["response_delay"] = self.response_start - self.start_time
            if self.wait_close:
                r["response_time"] = time.time() - self.start_time
                r["response_size"] = len(self.data)
        self.check.set_result(r)

    def get_request(self):
        return self.request
