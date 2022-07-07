# ----------------------------------------------------------------------
# SNMP Trap PDU Parser
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import base64

# NOC modules
from .ber import decode


class InvalidSNMPPacket(Exception):
    pass


class UnsupportedSNMPVersion(Exception):
    pass


def decode_trap(packet, raw=False):
    """
    :param packet:
    :param raw:
    :return:
    """
    version, community, pdu = decode(packet, include_raw=raw)
    raw_data = None
    if raw:
        raw_data = [
            {"oid": oid, "value": value, "value_raw":  base64.b64encode(value_raw).decode("utf-8")}
            for oid, value, value_raw in pdu[-1]
        ]
    decoder = PDU_PARSERS.get(version)
    if decoder is None:
        raise UnsupportedSNMPVersion("Unsupported SNMP version %s" % version)
    return community, decoder(pdu), raw_data


def decode_trap_pdu_v1(pdu):
    _, enterprise, agent_address, generic_type, specific_code, ts, varbinds = pdu
    r = {"1.3.6.1.6.3.1.1.4.1.0": enterprise}
    r.update(varbinds)
    return r


def decode_trap_pdu_v2c(pdu):
    return dict(pdu[-1])


PDU_PARSERS = {0: decode_trap_pdu_v1, 1: decode_trap_pdu_v2c}

VERSIONS = {0: "v1", 1: "v2c"}
