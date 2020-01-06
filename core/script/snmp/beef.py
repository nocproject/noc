# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SNMP Beef
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import socket

# Third-party modules
import tornado.gen
import tornado.iostream
from tornado.concurrent import TracebackFuture

# NOC modules
from noc.core.snmp.ber import BERDecoder, BEREncoder
from noc.core.snmp.consts import (
    PDU_GET_REQUEST,
    PDU_GETNEXT_REQUEST,
    PDU_GETBULK_REQUEST,
    PDU_RESPONSE,
)
from noc.core.snmp.error import NO_ERROR, NO_SUCH_NAME
from .base import SNMP


class BeefSNMP(SNMP):
    name = "beef_snmp"
    MAX_REQUEST_SIZE = 65535

    def __init__(self, script):
        super(BeefSNMP, self).__init__(script)
        self.server_iostream = None

    def get_socket(self):
        if not self.socket:
            c_socket, s_socket = socket.socketpair()
            self.socket = BeefClientIOStream(c_socket)
            self.server_iostream = BeefServerIOStream(s_socket, self.script)
            self.ioloop.add_callback(self.snmp_server)
        return self.socket

    def close(self):
        if self.server_iostream:
            self.server_iostream.close()
            self.server_iostream = None
        super(BeefSNMP, self).close()

    @tornado.gen.coroutine
    def snmp_server(self):
        """
        SNMP server coroutine
        :return:
        """
        self.logger.info("Stating BEEF SNMP server")
        yield self.server_iostream.connect()
        decoder = BERDecoder()
        encoder = BEREncoder()
        while True:
            # Wait for SNMP request
            request = yield self.server_iostream.read_bytes(self.MAX_REQUEST_SIZE, partial=True)
            pdu = decoder.parse_sequence(request)[0]
            self.logger.info("SNMP REQUEST: %r", pdu)
            version = pdu[0]
            community = pdu[1]
            pdu_type = pdu[2][0]
            request_id = pdu[2][1]
            if pdu_type == PDU_GET_REQUEST:
                err_status, err_index, data = self.snmp_get_response(pdu)
            elif pdu_type == PDU_GETNEXT_REQUEST:
                err_status, err_index, data = self.snmp_getnext_response(pdu)
            elif pdu_type == PDU_GETBULK_REQUEST:
                err_status, err_index, data = self.snmp_getbulk_response(pdu)
            else:
                # @todo: Unsupported PDU type
                pass
            # Build response
            resp = encoder.encode_sequence(
                [
                    encoder.encode_int(version),
                    encoder.encode_octet_string(community),
                    encoder.encode_choice(
                        PDU_RESPONSE,
                        [
                            encoder.encode_int(request_id),
                            encoder.encode_int(err_status),
                            encoder.encode_int(err_index),
                            encoder.encode_sequence(
                                [
                                    encoder.encode_sequence([encoder.encode_oid(str(oid)), value])
                                    for oid, value in data
                                ]
                            ),
                        ],
                    ),
                ]
            )
            self.logger.info("RESPONSE = %r", data)
            yield self.server_iostream.write(resp)

    def snmp_get_response(self, pdu):
        """
        Process SNMP GET request
        :param pdu: Parsed request PDU
        :return: error_status, error_index, varbinds
        """
        beef = self.script.request_beef()
        r = []
        err_status = NO_ERROR
        err_index = 0
        for n, oid in enumerate(pdu[2][-1]):
            v = beef.get_mib_value(oid[0])
            if v is None:
                # @todo: Error index
                if not err_index:
                    err_index = n + 1
                    err_status = NO_SUCH_NAME
                    v = "\x80"  # Missed instance
            r += [(oid[0], v)]
        return err_status, err_index, r

    def snmp_getnext_response(self, pdu):
        """
        Process SNMP GETNEXT request
        :param pdu: Parsed request PDU
        :return: error_status, error_index, varbinds
        """
        beef = self.script.request_beef()
        err_status = NO_ERROR
        err_index = 0
        start_oid = pdu[2][-1][0][0]
        r = []
        for oid in beef.iter_mib_oids(start_oid):
            if oid == start_oid:
                continue  # To next value
            r = [(oid, beef.get_mib_value(oid))]
            break
        # @todo: empty r == error
        return err_status, err_index, r

    def snmp_getbulk_response(self, pdu):
        """
        Process SNMP GETBULK request
        :param pdu: Parsed request PDU
        :return: error_status, error_index, varbinds
        """
        beef = self.script.request_beef()
        r = []
        err_status = NO_ERROR
        err_index = 0
        max_repetitions = pdu[2][3]
        start_oid = pdu[2][-1][0][0]
        for oid in beef.iter_mib_oids(start_oid):
            if oid == start_oid:
                continue  # To next value
            r += [(oid, beef.get_mib_value(oid))]
            if len(r) >= max_repetitions:
                break
        return err_status, err_index, r


class BeefServerIOStream(tornado.iostream.IOStream):
    def __init__(self, socket, script, *args, **kwargs):
        super(BeefServerIOStream, self).__init__(socket, *args, **kwargs)
        self.script = script

    def connect(self, *args, **kwargs):
        """
        Always connected
        :param args:
        :param kwargs:
        :return:
        """
        future = self._connect_future = TracebackFuture()
        # Force beef downloading
        beef = self.script.request_beef()
        if not beef:
            # Connection refused
            self.close(exc_info=True)
            return future
        future.set_result(True)
        # Start replying start state
        self._add_io_state(self.io_loop.WRITE)
        return future

    def close(self, exc_info=False):
        self.socket.close()
        self.socket = None


class BeefClientIOStream(tornado.iostream.IOStream):
    def get_timeout(self):
        return None

    def settimeout(self, timeout):
        return None

    @tornado.gen.coroutine
    def sendto(self, pdu, address):
        self._address = address
        self.socket.send(pdu)

    @tornado.gen.coroutine
    def recvfrom(self, buffsize):
        data = yield self.read_bytes(buffsize, partial=True)
        raise tornado.gen.Return((data, self._address))
