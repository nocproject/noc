##
## Event Collector Interface
##
import logging
class EventCollector(object):
    EVENT_SOURCE=None
    def __init__(self):
        self.filter={} # IP -> [(mask,action)]
    
    def set_event_filter(self,filter):
        logging.debug("set_event_filter(%s)"%",".join(["<%s, %s, %s>"%(ip,mask.pattern,repr(action)) for ip,mask,action in filter]))
        self.filter={}
        for ip,mask,callback in filter:
            if ip not in self.filter:
                self.filter[ip]=[(mask,callback)]
            else:
                self.filter[ip].append((mask,callback))
    
    def check_source_address(self,ip):
        if ip not in self.filter:
            logging.error("Invalid event source %s"%ip)
            return False
        return True
    
    def process_event(self,ip,message,body=None):
        for mask,action in self.filter[ip]:
            if mask.search(message):
                if action is None: # Ignore event
                    return
                action(source=self.EVENT_SOURCE,ip=ip,message=message,body=body)
