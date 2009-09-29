# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Collector Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import logging,time

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
            # Generate "Invalid event source" Event
            body={
                "source"   : "system",
                "component": "noc-activator",
                "activator": self.activator.activator_name,
                "collector": self.collector_signature,
                "type"     : "Invalid Event Source",
                "ip"       : ip
            }
            self.process_event(int(time.time()),"",body)
            return False
        return True
        
    def process_event(self,timestamp,ip,body={}):
        self.activator.on_event(timestamp,ip,body)

