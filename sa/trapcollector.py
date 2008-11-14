##
## SNMP Trap collector
##
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
import logging,asyncore,socket

class TrapCollector(asyncore.dispatcher):
    def __init__(self,activator,ip):
        asyncore.dispatcher.__init__(self)
        logging.info("Initializing trap collector")
        self.activator=activator
        self.ip=ip
        self.trap_filter={} # ip -> oid -> [action1, ..., actionN]
                            # def action(Trap)
        self.create_socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((ip,162))
    
    def set_trap_filter(self,trap_filter):
        logging.debug("trap collector: set trap filter: %s"%str(trap_filter))
        self.trap_filter=trap_filter.copy()
        
    def writable(self): return False
    
    def handle_connect(self): pass
    
    def handle_read(self):
        msg,transport_address=self.recvfrom(8192)
        if msg=="":
            return
        self.on_trap(transport_address,msg)

    def on_trap(self,transport_address,whole_msg):
        def oid_to_str(o):
            return ".".join([str(x) for x in o])
        address,port=transport_address
        if address not in self.trap_filter:
            logging.error("Trap from unknown address %s"%address)
            return
        while whole_msg:
            msg_version = int(api.decodeMessageVersion(whole_msg))
            if api.protoModules.has_key(msg_version):
                p_mod = api.protoModules[msg_version]
            else:
                logging.error('Unsupported SNMP version %s from %s'%(msg_version,transport_address))
                return
            req_msg,whole_msg=decoder.decode(whole_msg,asn1Spec=p_mod.Message())
            req_pdu = p_mod.apiMessage.getPDU(req_msg)
            if req_pdu.isSameTypeWith(p_mod.TrapPDU()):
                oid=oid_to_str(p_mod.apiTrapPDU.getEnterprise(req_pdu))
                if oid in self.trap_filter[address]:
                    for h in self.trap_filter[address][oid]:
                        h(address,oid)
                #print p_mod.apiTrapPDU.getAgentAddr(req_pdu)
                #print p_mod.apiTrapPDU.getGenericTrap(req_pdu)
                #print p_mod.apiTrapPDU.getSpecificTrap(req_pdu)
                #print p_mod.apiTrapPDU.getTimeStamp(req_pdu)
                #if msg_version == api.protoVersion1:
                #    varBinds = p_mod.apiTrapPDU.getVarBindList(req_pdu)
                #else:
                #    varBinds = p_mod.apiPDU.getVarBindList(req_pdu)
                #for oid, val in varBinds:
                #    print '%s = %s' % (oid, val)
        return whole_msg