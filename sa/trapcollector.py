##
## SNMP Trap collector
##
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from noc.lib.nbsocket import ListenUDPSocket
from noc.sa.eventcollector import EventCollector
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
    def __init__(self,activator,address,port):
        self.info("Initializing")
        ListenUDPSocket.__init__(self,activator.factory,address,port)
        EventCollector.__init__(self,activator)
        
    def on_read(self,whole_msg,address,port):
        def oid_to_str(o):
            return ".".join([str(x) for x in o])
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
                if msg_version==api.protoVersion1:
                    #oid=oid_to_str(p_mod.apiTrapPDU.getEnterprise(req_pdu))
                    var_binds=p_mod.apiTrapPDU.getVarBindList(req_pdu)
                else:
                    #oid=oid_to_str(p_mod.apiPDU.getEnterprise(req_pdu))
                    var_binds=p_mod.apiPDU.getVarBindList(req_pdu)
                    #oid="1"
                #self.debug("Trap from %s (%s)"%(address,oid))
                ts=int(time.time())
                body={
                    "source" : "SNMP Trap",
                    #"oid":oid,
                }
                for o,v in var_binds:
                    body[oid_to_str(o)]=v.prettyPrint().split("\n")[3].strip().split("=")[1]
                print body
                self.process_event(ts,address,body)
