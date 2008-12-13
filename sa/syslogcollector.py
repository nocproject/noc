##
## Syslog Collector
## (RFC3164)
##
from noc.lib.nbsocket import ListenUDPSocket
import logging,re

class SyslogCollector(ListenUDPSocket):
    def __init__(self,factory,address,port):
        logging.info("Initializing log collector")
        ListenUDPSocket.__init__(self,factory,address,port)
        self.log_filter={} # ip -> re -> [action1, ..., actionN]
        
    def set_log_filter(self,log_filter):
        logging.debug("log collector: set log filter: %s"%str(log_filter))
        self.log_filter=log_filter.copy()

    def on_read(self,msg,address,port):
        if address not in self.log_filter:
            logging.error("Syslog from unknown address %s"%address)
            return
        if msg.startswith("<"):
            idx=msg.find(">")
            if idx==-1:
                return
            msg=msg[idx+1:]
            # TODO: Parse timestamp
        for r in self.log_filter[address]:
            if re.search(r,msg,re.I):
                for h in self.log_filter[address][r]:
                    h(address,msg)
