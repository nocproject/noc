##
## Syslog Collector
## (RFC3164)
##
from noc.lib.nbsocket import ListenUDPSocket
import logging
from noc.sa.eventcollector import EventCollector
from noc.sa.protocols.sae_pb2 import ES_SYSLOG

class SyslogCollector(ListenUDPSocket,EventCollector):
    EVENT_SOURCE=ES_SYSLOG
    def __init__(self,factory,address,port):
        logging.info("Initializing log collector")
        ListenUDPSocket.__init__(self,factory,address,port)
        EventCollector.__init__(self)
        
    def on_read(self,msg,address,port):
        if not self.check_source_address(address):
            return
        if msg.startswith("<"):
            idx=msg.find(">")
            if idx==-1:
                return
            msg=msg[idx+1:]
            # TODO: Parse timestamp
        self.process_event(address,msg)
