# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SLA Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
import time,re
##
## Probe registry
##
class ProbeRegistry(Registry):
    name="ProbeRegistry"
    subdir="probes"
    classname="Probe"
    apps=["noc.pm"]
probe_registry=ProbeRegistry()
##
## Metaclass for Probe
##
class ProbeBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        m.scripts={}
        probe_registry.register(m.name,m)
        return m
##
PR_OK   = 0
PR_WARN = 1
PR_FAIL = 2
##
class Param(object):
    def __init__(self,probe,name,description):
        self.probe=probe
        self.name=name
        # Copy thresholds from descriptions
        if "threshold" in description:
            self.threshold=description["threshold"].copy()
        else:
            self.threshold={}
        # Read thresholds from config
        rx=re.compile(r"^threshold\.(?P<category>fail|warn)\.(?P<type>high|low)\.%s$"%self.name)
        for opt in self.probe.config.options(self.probe.probe_name):
            match=rx.match(opt)
            if match:
                if match.group("category") not in self.threshold:
                    self.threshold[match.group("category")]={}
                self.threshold[match.group("category")][match.group("type")]=self.probe.config.getfloat(self.probe.probe_name,opt)
    def __repr__(self):
        return "<Param %s %s>"%(self.name,str(self.threshold))
        
    # Checks value agains thresholds
    def check(self,value):
        if "fail" in self.threshold\
            and (("low" in self.threshold["fail"] and self.threshold["fail"]["low"]>value)\
                or ("high" in self.threshold["fail"] and self.threshold["fail"]["high"]<value)):
            return PR_FAIL,"%s hits failure thresholds"%self.name
        if "warn" in self.threshold\
            and (("low" in self.threshold["warn"] and self.threshold["warn"]["low"]>value)\
                or ("high" in self.threshold["warn"] and self.threshold["warn"]["high"]<value)):
            return PR_WARN,"%s hits warning thresholds"%self.name
        return PR_OK,"OK"
##
class Result(object):
    def __init__(self,probe,service,result,message=""):
        self.probe_name=probe.probe_name
        self.probe_type=probe.probe_type
        self.timestamp=int(time.time())
        self.service=service
        self.result=result
        self.message=message
    
    def fill_pmresult(self,r):
        r.probe_name=self.probe_name
        r.probe_type=self.probe_type
        r.timestamp=self.timestamp
        r.service=self.service
        r.result=self.result
        r.message=self.message
##
rx_threshold=re.compile("^threshold.(?P<category>fail|warn).(?P<type>high|low).(?P<name>.+)$")
##
## SLA Probe
##
class Probe(object):
    __metaclass__=ProbeBase
    name=None
    parameters={} # Name -> {"threshold" : ....}
    def __init__(self,daemon,probe_name,config):
        self.daemon=daemon
        self.probe_name=probe_name
        self.probe_type=self.name
        self.factory=self.daemon.factory
        self.config=config
        self.interval=self.config.getint(self.probe_name,"interval")
        self.services=[x.strip() for x in self.config.get(self.probe_name,"services").strip().split(",")]
        self.params={}
        for name,pd in self.parameters.items():
            self.params[name]=Param(self,name,pd)
        self.start_time=None
        self.next_run=time.time()
        self.pm_result={} # service -> (timestamp,PR_OK|PR_ERR|PR_FAIL)
        self.pm_data={}   # service -> [(timestamp,param,value)]
    
    def __cmp__(self,y):
        return cmp(self.next_run,y.next_run)

    def start(self):
        self.start_time=time.time()
        self.pm_result={}
        self.pm_data={}
        self.on_start()
    
    def stop(self):
        self.on_stop()
    
    def set_data(self,service,param,value):
        name="%s.%s.%s"%(service,self.probe_name,param)
        t=int(time.time())
        if service not in self.pm_data:
            self.pm_data[service]=[(t,name,value)]
        else:
            self.pm_data[service]+=[(t,name,value)]
        result,message=self.params[param].check(value)
        self.set_result(service,result,message)
    
    def set_result(self,service,result,message="OK"):
        r=Result(self,service,result,message)
        if service not in self.pm_result:
            self.pm_result[service]=r
            return
        if result>self.pm_result[service].result: # Error escalation
            if self.pm_result[service].result==PR_OK:
                r.message=message
            else:
                r.message="%s, %s"%(self.pm_result[service].message,message)
            self.pm_result[service]=r
    
    def exit(self):
        self.next_run=self.start_time+self.interval
        self.start_time=None
        data=[]
        for v in self.pm_data.values():
            data+=v
        self.daemon.exit_probe(self,self.pm_result.values(),data)
    
    def _is_active(self):
        return self.start_time is not None
    is_active=property(_is_active)
    
    def _is_stale(self):
        return self.start_time+self.interval<time.time()
    is_stale=property(_is_stale)
    
    def _ready_to_run(self):
        return self.next_run<time.time()
    ready_to_run=property(_ready_to_run)
    ##
    ##
    ##
    def on_start(self):
        pass
    ##
    ##
    ##
    def on_stop(self):
        pass
