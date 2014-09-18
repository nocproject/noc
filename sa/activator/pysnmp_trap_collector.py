# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP Trap Collector with pysnmp trap parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python module
import time
import logging
## pysnmp modules
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
## NOC modules
from noc.lib.nbsocket import ListenUDPSocket
from noc.sa.activator.event_collector import EventCollector
from noc.lib.escape import fm_escape


class TrapCollector(ListenUDPSocket, EventCollector):
    """
    SNMP Trap collector.

    Body structure:
    {
        "source": "SNMP Trap",
        "oid": "trap oid",
        "oid": "value"
        ....
    }
    """
    name = "TrapCollector"

    def __init__(self, activator, address, port, log_traps=False):
        self.collector_signature = "%s:%s" % (address, port)
        self.log_traps = log_traps
        ListenUDPSocket.__init__(self, activator.factory, address, port)
        EventCollector.__init__(self, activator)
        self.logger.info("Initializing")

    def on_read(self, whole_msg, address, port):
        def oid_to_str(o):
            return ".".join([str(x) for x in o])

        def extract(val):
            def unchain(val):
                c = []
                for i in range(len(val._componentValues)):
                    k = val._componentValues[i]
                    if k is not None:
                        if hasattr(k, "getComponentType"):
                            c.append(k.getComponentType().getNameByPosition(i))
                            c.extend(unchain(k))
                        elif hasattr(k, "_value"):
                            c.append(k._value)
                return c

            v = unchain(val)
            if not v:
                return ""
            v = v[-1]
            if type(v) == tuple:
                return oid_to_str(v)
            return fm_escape(v)

        object = self.map_event(address)
        if not object:
            # Skip events from unknown sources
            return
        if self.log_traps:
            self.logger.debug("SNMP TRAP: %r", whole_msg)
        while whole_msg:
            msg_version = int(api.decodeMessageVersion(whole_msg))
            if api.protoModules.has_key(msg_version):
                p_mod = api.protoModules[msg_version]
            else:
                self.logger.error('Unsupported SNMP version %s from %s',
                                  msg_version, address)
                return
            req_msg, whole_msg = decoder.decode(whole_msg,
                                                asn1Spec=p_mod.Message())
            req_pdu = p_mod.apiMessage.getPDU(req_msg)
            if req_pdu.isSameTypeWith(p_mod.TrapPDU()):
                body = {
                    "source":"SNMP Trap","collector":
                    self.collector_signature
                }
                if msg_version == api.protoVersion1:
                    oid = oid_to_str(p_mod.apiTrapPDU.getEnterprise(req_pdu))
                    body["1.3.6.1.6.3.1.1.4.1.0"] = oid  # snmpTrapOID.0
                    var_binds = p_mod.apiTrapPDU.getVarBindList(req_pdu)
                else:
                    var_binds = p_mod.apiPDU.getVarBindList(req_pdu)
                ts = int(time.time())
                for o, v in var_binds:
                    body[oid_to_str(o._value)] = extract(v)
                if self.log_traps:
                    self.logger.debug("DECODED SNMP TRAP: %s", body)
                self.process_event(ts, object, body)
