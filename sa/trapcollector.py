##
## SNMP Trap collector
##
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from noc.lib.nbsocket import ListenUDPSocket
import logging
from noc.sa.eventcollector import EventCollector
from noc.sa.protocols.sae_pb2 import ES_SNMP_TRAP

class TrapCollector(ListenUDPSocket,EventCollector):
    EVENT_SOURCE=ES_SNMP_TRAP
    def __init__(self,factory,address,port):
        logging.info("Initializing trap collector")
        ListenUDPSocket.__init__(self,factory,address,port)
        EventCollector.__init__(self)
        
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
                logging.error('Unsupported SNMP version %s from %s'%(msg_version,address))
                return
            req_msg,whole_msg=decoder.decode(whole_msg,asn1Spec=p_mod.Message())
            req_pdu = p_mod.apiMessage.getPDU(req_msg)
            if req_pdu.isSameTypeWith(p_mod.TrapPDU()):
                oid=oid_to_str(p_mod.apiTrapPDU.getEnterprise(req_pdu))
                logging.debug("Trap from %s (%s)"%(address,oid))
                self.process_event(address,oid)
