# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SNMP SET PDU generator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import random
# NOC modules
from .ber import BEREncoder
from .consts import PDU_SET_REQUEST
from .version import SNMP_v1, SNMP_v2c


def set_pdu(community, varbinds, request_id=None, version=SNMP_v2c):
    """
    Generate SNMP v2c SET PDU
    :param version:
    :param community:
    :param varbinds: List of (oid, value)
    :return:
    """
    if version != SNMP_v1 and version != SNMP_v2c:
        raise NotImplementedError("Unsupported SNMP version")
    e = BEREncoder()
    if not request_id:
        request_id = random.randint(0, 0x7FFFFFFF)
    # Encode variable bindings
    vbs = []
    for oid, value in varbinds:
        if value is None:
            v = e.encode_null()
        elif isinstance(value, basestring):
            v = e.encode_octet_string(value)
        elif isinstance(value, (int, long)):
            v = e.encode_int(value)
        else:
            raise ValueError("Unknown varbind type")
        vbs += [
            e.encode_sequence([e.encode_oid(oid), v])
        ]
    varbinds = e.encode_sequence(vbs)
    # Encode RFC-1905 SNMP SET PDU
    pdu = e.encode_choice(PDU_SET_REQUEST, [
        e.encode_int(request_id),
        e.encode_int(0),  # Error status
        e.encode_int(0),  # Error index
        varbinds
    ])
    # SNMP v2c PDU
    return e.encode_sequence([
        e.encode_int(version),
        e.encode_octet_string(community),
        pdu
    ])
