# ----------------------------------------------------------------------
# SNMP GET PDU generator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
from collections import namedtuple

# NOC modules
from .ber import parse_p_oid, BERDecoder, encoder
from .consts import PDU_GET_REQUEST, PDU_GETNEXT_REQUEST, PDU_RESPONSE, PDU_GETBULK_REQUEST
from .version import SNMP_v1, SNMP_v2c


def _build_pdu(community, pdu_type, oids, request_id, version=SNMP_v2c):
    """
    Generate SNMP v2c GET/GETNEXT
    :param version:
    :param community:
    :param oids:
    :return:
    """
    if version != SNMP_v1 and version != SNMP_v2c:
        raise NotImplementedError("Unsupported SNMP version")
    if not request_id:
        request_id = random.randint(0, 0x7FFFFFFF)
    # Encode variable bindings
    varbinds = encoder.encode_sequence(
        [
            encoder.encode_sequence([encoder.encode_oid(str(oid)), encoder.encode_null()])
            for oid in oids
        ]
    )
    # Encode RFC-1905 SNMP GET PDU
    pdu = encoder.encode_choice(
        pdu_type,
        [
            encoder.encode_int(request_id),
            encoder.encode_int(0),  # Error status
            encoder.encode_int(0),  # Error index
            varbinds,
        ],
    )
    # SNMP v2c PDU
    return encoder.encode_sequence(
        [encoder.encode_int(version), encoder.encode_octet_string(str(community)), pdu]
    )


def get_pdu(community, oids, request_id=None, version=SNMP_v2c):
    """
    Generate SNMP v2c GET PDU
    :param version:
    :param community:
    :param oids:
    :return:
    """
    return _build_pdu(community, PDU_GET_REQUEST, oids, request_id, version)


def getnext_pdu(community, oid, request_id=None, version=SNMP_v2c):
    """
    Generate SNMP v2c GETNEXT PDU
    :param version:
    :param community:
    :param oids:
    :return:
    """
    return _build_pdu(community, PDU_GETNEXT_REQUEST, [oid], request_id, version)


def getbulk_pdu(
    community, oid, request_id=None, non_repeaters=0, max_repetitions=10, version=SNMP_v2c
):
    """
    Generate SNMP v2c GETBULK PDU
    """
    if version == SNMP_v1:
        raise ValueError("SNMPv1 does not define GETBULK")
    if not request_id:
        request_id = random.randint(0, 0x7FFFFFFF)
    oids = [oid]
    # Encode variable bindings
    varbinds = encoder.encode_sequence(
        [encoder.encode_sequence([encoder.encode_oid(o), encoder.encode_null()]) for o in oids]
    )
    # Encode RFC-1905 SNMP GET PDU
    pdu = encoder.encode_choice(
        PDU_GETBULK_REQUEST,
        [
            encoder.encode_int(request_id),
            encoder.encode_int(non_repeaters),
            encoder.encode_int(max_repetitions),
            varbinds,
        ],
    )
    # SNMP v2c PDU
    return encoder.encode_sequence(
        [encoder.encode_int(SNMP_v2c), encoder.encode_octet_string(community), pdu]
    )


GetResponse = namedtuple(
    "GetResponse", ["community", "request_id", "error_status", "error_index", "varbinds"]
)


def parse_get_response(pdu, display_hints=None):
    decoder = BERDecoder(display_hints=display_hints)
    data = decoder.parse_sequence(pdu)[0]
    pdu = data[2]
    if pdu[0] != PDU_RESPONSE:
        raise ValueError("Invalid response PDU type: %s" % pdu[0])
    return GetResponse(
        community=data[1],
        request_id=pdu[1],
        error_status=pdu[2],
        error_index=pdu[3],
        varbinds=pdu[4],
    )


def parse_get_response_raw(pdu):
    decoder = BERDecoder()
    # Strip outer sequence
    msg, _ = decoder.split_tlv(pdu)
    # Strip proto version
    _, msg = decoder.split_tlv(msg)
    # Strip community
    _, msg = decoder.split_tlv(msg)
    # Strip inner sequence
    msg, _ = decoder.split_tlv(msg)
    # Strip pdu type
    _, msg = decoder.split_tlv(msg)
    # strip request id
    _, msg = decoder.split_tlv(msg)
    # strip error_code
    _, msg = decoder.split_tlv(msg)
    # strip error_index
    msg, _ = decoder.split_tlv(msg)
    # Varbinds
    varbinds = []
    while msg:
        vb, msg = decoder.split_tlv(msg)
        oid, value = decoder.split_tlv(vb)
        varbinds += [[parse_p_oid(oid), value]]
    data = decoder.parse_sequence(pdu)[0]
    pdu = data[2]
    if pdu[0] != PDU_RESPONSE:
        raise ValueError("Invalid response PDU type: %s" % pdu[0])
    return GetResponse(
        community=data[1],
        request_id=pdu[1],
        error_status=pdu[2],
        error_index=pdu[3],
        varbinds=varbinds,
    )
