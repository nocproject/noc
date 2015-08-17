# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Graphite Line Collector Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import tornado.tcpserver
import tornado.iostream
import tornado.gen


class GraphiteCollector(tornado.tcpserver.TCPServer):
    MAX_LINE = 1024

    def __init__(self, service, *args, **kwargs):
        super(GraphiteCollector, self).__init__(*args, **kwargs)
        self.service = service

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        while True:
            try:
                data = yield stream.read_until("\n", max_bytes=self.MAX_LINE)
            except tornado.iostream.StreamClosedError:
                break
            try:
                metric, value, timestamp = data.split()
                value = float(value)
                timestamp = float(timestamp)
            except ValueError, why:
                self.service.logger.error("Invalid PDU: %s (%r)", why, data)
                continue  # Invalid PDU
            self.service.spool_metric(metric, timestamp, value)
