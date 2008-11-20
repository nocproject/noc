##
## SNMP Trap collector
##
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from noc.lib.nbsocket import ListenUDPSocket
import logging

class TrapCollector(ListenUDPSocket):
    logging.info("Initializing trap collector")
    def __init__(self,factory,address,port):
        ListenUDPSocket.__init__(self,factory,address,port)
        self.trap_filter={} # ip -> oid -> [action1, ..., actionN]
                            # def action(Trap)
    
    def set_trap_filter(self,trap_filter):
        logging.debug("trap collector: set trap filter: %s"%str(trap_filter))
        self.trap_filter=trap_filter.copy()
        
    def on_read(self,whole_msg,address,port):
        def oid_to_str(o):
            return ".".join([str(x) for x in o])
        if address not in self.trap_filter:
            logging.error("Trap from unknown address %s"%address)
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
                if oid in self.trap_filter[address]:
                    for h in self.trap_filter[address][oid]:
                        h(address,oid)