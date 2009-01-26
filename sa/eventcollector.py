##
## Event Collector Interface
##
import logging
class EventCollector(object):
    name="EventCollector"
    def __init__(self,activator):
        self.activator=activator
    
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.name,msg))
    
    def info(self,msg):
        logging.info("[%s] %s"%(self.name,msg))
    
    def error(self,msg):
        logging.error("[%s] %s"%(self.name,msg))
        
    def check_source_address(self,ip):
        if not self.activator.check_event_source(ip):
            self.error("Invalid event source %s"%ip)
            return False
        return True
        
    def process_event(self,timestamp,ip,body={}):
        self.activator.on_event(timestamp,ip,body)

