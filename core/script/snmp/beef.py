# ----------------------------------------------------------------------
# SNMP Beef
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple

# NOC modules
from noc.core.snmp.ber import BERDecoder, BEREncoder
from noc.core.snmp.consts import (
    PDU_GET_REQUEST,
    PDU_GETNEXT_REQUEST,
    PDU_GETBULK_REQUEST,
    PDU_RESPONSE,
)
from noc.core.snmp.error import NO_ERROR, NO_SUCH_NAME, END_OID_TREE
from noc.core.script.error import ScriptError
from noc.core.comp import smart_bytes
from .base import SNMP


class BeefSNMP(SNMP):
    name = "beef_snmp"

    def get_socket(self):
        if not self.socket:
            self.socket = BeefSNMPSocket(self)
        return self.socket


class BeefSNMPSocket(object):
    def __init__(self, snmp):
        self.script = snmp.script
        self.logger = snmp.logger
        if not self.script.request_beef():
            raise ScriptError("Beef not found")

    def close(self):
        self.script = None
        self.logger = None

    async def send_and_receive(
        self, data: bytes, address: Tuple[str, int]
    ) -> Tuple[bytes, Tuple[str, int]]:
        pdu = BERDecoder().parse_sequence(data)[0]
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
            raise ScriptError("Unknown PDU type")
        # Build response
        encoder = BEREncoder()
        response = encoder.encode_sequence(
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
                                encoder.encode_sequence(
                                    [encoder.encode_oid(str(oid)), smart_bytes(value)]
                                )
                                for oid, value in data
                            ]
                        ),
                    ],
                ),
            ]
        )
        self.logger.info("RESPONSE = %r", data)
        return response, address

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
        if not r:
            err_status = END_OID_TREE
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
        if not r:
            err_status = END_OID_TREE
        return err_status, err_index, r
