# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QFC
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python module
import re

# NOC module
from noc.core.profile.base import BaseProfile
from noc.core.snmp.get import GetResponse, BERDecoder, PDU_RESPONSE


def parse_get_response(pdu: bytes, display_hints=None) -> GetResponse:
    """
    Common response parser
    :param pdu:
    :param display_hints:
    :return:
    """
    decoder = BERDecoder(display_hints=display_hints)
    data = decoder.parse_sequence(pdu)[0]
    pdu = data[2]
    if pdu[0] != PDU_RESPONSE:
        raise ValueError("Invalid response PDU type: %s" % pdu[0])
    error_index = pdu[3]
    if pdu[2]:
        # Always get 1 OID on query. If error return bad value
        error_index = 1
    return GetResponse(
        community=data[1],
        request_id=pdu[1],
        error_status=pdu[2],
        error_index=error_index,
        varbinds=pdu[4],
    )


class Profile(BaseProfile):
    """
    Supported two device revision - V2 and V3:
    V2 - Monitoring controller. May worked as battery controller, and has RS485 port
    for transparent connect device or Energy meter connected
    V3 - Monitoring and UPS controller, additional have RS232 port
     for connect to UPS supported  Megatec, CyberPower Protocol II proto

     V2 - 1.3.6.1.4.1.27514.102 MIB Tree
     V3 - 1.3.6.1.4.1.27514.103 MIB Tree
    """

    name = "Qtech.QFC"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 1
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    snmp_response_parser = parse_get_response  # For error_index return bad value

    matchers = {
        "is_lite": {"platform": {"$regex": "QFC-PBIC-LITE"}},
    }

    rx_interface_name = re.compile(r"^\d+$")
