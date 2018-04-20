# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP GET PDU generator
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
from collections import namedtuple
## NOC modules
from ber import BEREncoder, BERDecoder
from consts import (SNMP_v2c, PDU_GET_REQUEST, PDU_GETNEXT_REQUEST,
                    PDU_RESPONSE, PDU_GETBULK_REQUEST)


def _build_pdu(community, pdu_type, oids, request_id):
    """
    Generate SNMP v2c GET/GETNEXT
    :param version:
    :param community:
    :param oids:
    :return:
    """
    e = BEREncoder()
    if not request_id:
        request_id = random.randint(0, 0x7FFFFFFF)
    # Encode variable bindings
    varbinds = e.encode_sequence([
        e.encode_sequence([
            e.encode_oid(oid),
            e.encode_null()
        ]) for oid in oids
    ])
    # Encode RFC-1905 SNMP GET PDU
    pdu = e.encode_choice(pdu_type, [
        e.encode_int(request_id),
        e.encode_int(0),  # Error status
        e.encode_int(0),  # Error index
        varbinds
    ])
    # SNMP v2c PDU
    return e.encode_sequence([
        e.encode_int(SNMP_v2c),
        e.encode_octet_string(community),
        pdu
    ])


def get_pdu(community, oids, request_id=None):
    """
    Generate SNMP v2c GET PDU
    :param version:
    :param community:
    :param oids:
    :return:
    """
    return _build_pdu(community, PDU_GET_REQUEST, oids, request_id)


def getnext_pdu(community, oid, request_id=None):
    """
    Generate SNMP v2c GETNEXT PDU
    :param version:
    :param community:
    :param oids:
    :return:
    """
    return _build_pdu(community, PDU_GETNEXT_REQUEST, [oid], request_id)


def getbulk_pdu(community, oid, request_id=None,
                non_repeaters=0, max_repetitions=10):
    """
    Generate SNMP v2c GETBULK PDU
    """
    e = BEREncoder()
    if not request_id:
        request_id = random.randint(0, 0x7FFFFFFF)
    oids = [oid]
    # Encode variable bindings
    varbinds = e.encode_sequence([
        e.encode_sequence([
            e.encode_oid(oid),
            e.encode_null()
        ]) for oid in oids
    ])
    # Encode RFC-1905 SNMP GET PDU
    pdu = e.encode_choice(PDU_GETBULK_REQUEST, [
        e.encode_int(request_id),
        e.encode_int(non_repeaters),
        e.encode_int(max_repetitions),
        varbinds
    ])
    # SNMP v2c PDU
    return e.encode_sequence([
        e.encode_int(SNMP_v2c),
        e.encode_octet_string(community),
        pdu
    ])


GetResponse = namedtuple("GetResponse", ["community", "request_id",
                                         "error_status", "error_index",
                                         "varbinds"])


def parse_get_response(pdu):
    d = BERDecoder()
    data = d.parse_sequence(pdu)[0]
    pdu = data[2]
    if pdu[0] != PDU_RESPONSE:
        raise ValueError("Invalid response PDU type: %s" % pdu[0])
    return GetResponse(
        community=data[1],
        request_id=pdu[1],
        error_status=pdu[2],
        error_index=pdu[3],
        varbinds=pdu[4]
    )
