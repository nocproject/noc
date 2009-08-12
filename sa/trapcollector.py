# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP Trap Collector
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from noc.lib.nbsocket import ListenUDPSocket
from noc.sa.eventcollector import EventCollector
from noc.lib.pyquote import bin_quote
import time

##
## Body has following structure:
## {
## "source"   : "SNMP trap"
## "oid"      : <trap oid>
## "left oid" : <right value>
## }
##
class TrapCollector(ListenUDPSocket,EventCollector):
    name="TrapCollector"
    def __init__(self,activator,address,port):
        self.info("Initializing at %s:%s"%(address,port))
        self.collector_signature="%s:%s"%(address,port)
        ListenUDPSocket.__init__(self,activator.factory,address,port)
        EventCollector.__init__(self,activator)
        
    def on_read(self,whole_msg,address,port):
        def oid_to_str(o):
            return ".".join([str(x) for x in o])
        def extract(val):
            def unchain(val): 
                c = []
                for i in range(len(val._componentValues)):
                    k=val._componentValues[i]
                    if k is not None:
                        if hasattr(k,"getComponentType"):
                            c.append(k.getComponentType().getNameByPosition(i))
                            c.extend(unchain(k))
                        elif hasattr(k,"_value"):
                            c.append(k._value)
                return c
                
            v=unchain(val)
            if len(v)==0:
                return ""
            v=v[-1]
            if type(v)==tuple:
                return oid_to_str(v)
            return bin_quote(str(v))

        if not self.check_source_address(address):
            return
        while whole_msg:
            msg_version = int(api.decodeMessageVersion(whole_msg))
            if api.protoModules.has_key(msg_version):
                p_mod = api.protoModules[msg_version]
            else:
                self.error('Unsupported SNMP version %s from %s'%(msg_version,address))
                return
            req_msg,whole_msg=decoder.decode(whole_msg,asn1Spec=p_mod.Message())
            req_pdu = p_mod.apiMessage.getPDU(req_msg)
            if req_pdu.isSameTypeWith(p_mod.TrapPDU()):
                body={"source":"SNMP Trap","collector":self.collector_signature}
                if msg_version==api.protoVersion1:
                    oid=oid_to_str(p_mod.apiTrapPDU.getEnterprise(req_pdu))
                    body["1.3.6.1.6.3.1.1.4.1.0"]=oid # snmpTrapOID.0
                    var_binds=p_mod.apiTrapPDU.getVarBindList(req_pdu)
                else:
                    var_binds=p_mod.apiPDU.getVarBindList(req_pdu)
                ts=int(time.time())
                for o,v in var_binds:
                    body[oid_to_str(o._value)]=extract(v)
                self.process_event(ts,address,body)
