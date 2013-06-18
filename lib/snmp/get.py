# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP GET PDU generator
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
## NOC modules
from ber import BEREncoder


def get_pdu(community, oids, request_id=None):
    """
    Generate SNMP v2c GET PDU
    :param version:
    :param community:
    :param oids:
    :return:
    """
    e = BEREncoder()
    if not request_id:
        request_id = random.randint(0, 0xFFFFFFFF)
    # Encode variable bindings
    varbinds = e.encode_sequence([
        e.encode_sequence([
            e.encode_oid(oid),
            e.encode_null()
        ]) for oid in oids
    ])
    # Encode RFC-1905 SNMP GET PDU
    pdu = e.encode_implicit_constructed([
        e.encode_int(request_id),
        e.encode_int(0),  # Error status
        e.encode_int(0),  # Error index
        varbinds
    ])
    # SNMP v2c PDU
    return e.encode_sequence([
        e.encode_int(1),
        e.encode_octet_string(community),
        pdu
    ])


