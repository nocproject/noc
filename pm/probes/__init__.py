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
import time,re,logging
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
## Param types
PT_GAUGE = 0
PT_COUNTER = 1

PT_MAP={
    "gauge"   : PT_GAUGE,
    "counter" : PT_COUNTER
}

MAX_COUNTER_32=4294967296.0
MAX_COUNTER_64=18446744073709551616.0
##
## Probe parameter
## Performs value cleaning and threshold checking
## Each probe parameter leads to one Time Series
##
class Param(object):
    def __init__(self,probe,name,description):
        self.probe=probe
        self.name=name
        self.last_time=None
        self.last_value=None
        self.description=description
        # Set parameter type
        if "type" in description:
            try:
                self.type=PT_MAP[description["type"]]
            except KeyError:
                raise "Invalid param type %s"%description["type"]
        else:
            self.type=PT_GAUGE
        # Set scale
        self.scale=description.get("scale",1.0)
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
                self.threshold[match.group("category")][match.group("type")]=self.probe.getfloat(opt)
    ##
    def __repr__(self):
        return "<Param %s %s>"%(self.name,str(self.description))
    ##    
    ## Checks value agains thresholds
    ## Returns (Result,message,cleaned_value)
    ##
    def clean(self,t,value):
        if value is None:
            return PR_FAIL,"Failed to retrieve parameter '%s'"%self.name,None
        # PT_COUNTER returns relative difference against previous value
        if self.type==PT_COUNTER:
            if not self.last_time:
                self.last_time=t
                self.last_value=value
                return PR_OK,"OK",None
            if value>=self.last_value:
                v=(value-self.last_value)/(t-self.last_time)
            else:
                # Handle wrapping
                self.probe.debug("Counter wrapping fixed")
                mc=MAX_COUNTER_64 if self.last_value>MAX_COUNTER_32 else MAX_COUNTER_32
                v=(value+(mc-self.last_value))/(t-self.last_time)
            self.last_time=t
            self.last_value=value
            value=v
        value*=self.scale
        # Check cleaned value thresholds
        if "fail" in self.threshold\
            and (("low" in self.threshold["fail"] and self.threshold["fail"]["low"]>value)\
                or ("high" in self.threshold["fail"] and self.threshold["fail"]["high"]<value)):
            return PR_FAIL,"%s hits failure thresholds"%self.name,value
        if "warn" in self.threshold\
            and (("low" in self.threshold["warn"] and self.threshold["warn"]["low"]>value)\
                or ("high" in self.threshold["warn"] and self.threshold["warn"]["high"]<value)):
            return PR_WARN,"%s hits warning thresholds"%self.name,value
        return PR_OK,"OK",value
##
## Check result
## Each probe will generate one result per check
## Result will became FM event after wire transmission
##
class Result(object):
    def __init__(self,probe,service,result,message=""):
        self.probe_name=probe.probe_name
        self.probe_type=probe.probe_type
        self.timestamp=int(time.time())
        self.service=service
        self.result=result
        self.message=message
    ##
    ## Fill Protocol structure
    ##
    def fill_pmresult(self,r):
        r.probe_name=self.probe_name
        r.probe_type=self.probe_type
        r.timestamp=self.timestamp
        r.service=self.service
        r.result=self.result
        r.message=self.message
##
rx_var=re.compile(r"{{\S+}}")
rx_range=re.compile(r"\[\s*(\d+)\s*-\s*(\d+)\s*\]")
## Probe
## Probe collects defined set of parameter's values for all of its services
## and perform thresholds checking.
##
## This is abstract class to be extended in subclasses.
## Subclass must implement at least two methods
##   * on_start() - Launch new round of checks
##   * on_stop() - Triggered when probe timeout expired. stop() method must terminate all incomplete checks and return failure for them
## Subclasses must follow non-blocking behavior as long as it possible using provided non-blocking fabric
##
## Description is a hash, containing optional parameters
##
## type -> counter|gauge - Parameter type. gauge will be written as-is, counter will be written as relative difference with previous value
## threshold -> warn|fail -> low|high -> value. Parameter's warn|fail, low|high thresholds
class Probe(object):
    __metaclass__=ProbeBase
    name=None
    parameters={} # Name -> description
    def __init__(self,daemon,probe_name,config):
        self.daemon=daemon
        self.probe_name=probe_name
        self.probe_type=self.name
        self.factory=self.daemon.factory
        self.config=config
        self.interval=self.getint("interval",60)
        self.services=self.expand_config_list("services")
        self.params={}
        if not self.delay_parameter_expansion():
            self.expand_parameters()
        self.start_time=None
        self.next_run=time.time()
        self.pm_result={} # service -> (timestamp,PR_OK|PR_ERR|PR_FAIL)
        self.pm_data={}   # service -> [(timestamp,param,value)]
        self.info("Initialized")
    ##
    ## Probes are ordereb by next_run properties
    ##
    def __cmp__(self,y):
        return cmp(self.next_run,y.next_run)
    ##
    ## Read configuration option containing comma-separated list of values
    ## and return list object
    ##
    def expand_config_list(self,name):
        l=[]
        if self.config.has_option(self.probe_name,name):
            for opt in [x.strip() for x in self.get(name).split(",") if x.strip()]:
                match=rx_range.search(opt)
                if match:
                    # Expand range expression: [d1-d2]
                    d1=int(match.group(1))
                    d2=int(match.group(2))
                    if d1>d2:
                        v=d1
                        d1=d2
                        d2=v
                    for i in range(d1,d2+1):
                        l+=[rx_range.sub(str(i),opt)]
                else:
                    l+=[opt]
        return l
    ##
    ## Must Parameter object be generated by Probe constructor or
    ## they will be generated later by subclass
    ##
    def delay_parameter_expansion(self):
        return False
    ##
    ## Generate Parameter object for given serive, name and description
    ## If parameter name contains {{var}} substring,
    ## config file must contain option 'var' with list of values (i.e. v1, v2, v3)
    ## and a set of parameters will be generated for each of the values
    ##
    def expand_parameter(self,service,name,description):
        match=rx_var.search(name)
        if match:
            var_name=match.group(1)
            for var in self.expand_config_list(var_name):
                n="%s.%s.%s"%(service,self.probe_name,name.replace("{{%s}}"%var_name,var))
                self.params[n]=Param(self,n,description)
        else:
            n="%s.%s.%s"%(service,self.probe_name,name)
            self.params[n]=Param(self,n,description)
    ##
    ## Expands class parameters and performes variables substitution
    ## Called from constructor when delay_parameter_expansions() returns false.
    ## Read class parameters description
    ##
    def expand_parameters(self):
        for name,description in self.parameters.items():
            for service in self.services:
                self.expand_parameter(service,name,description)
    ##
    ## Start new check round.
    ## Called by noc-probe.
    ## start() calls on_start() method which overriden in subclasses
    ##
    def start(self):
        self.debug("Start")
        self.start_time=time.time()
        self.pm_result={}
        self.pm_data={}
        self.on_start()
    ##
    ## Stop probe
    ## Called by noc-probe when probe timeout expired
    ##
    def stop(self):
        self.debug("Stop")
        self.on_stop()
    ##
    ## Called by subclasses. Stores value of the service's parameter
    ## in the output queue
    ##
    def set_data(self,service,param,value):
        # Clean parameters
        name="%s.%s.%s"%(service,self.probe_name,param)
        t=int(time.time())
        result,message,value=self.params[name].clean(t,value)
        # Enqueue data
        if service not in self.pm_data:
            self.pm_data[service]=[(t,name,value)]
        else:
            self.pm_data[service]+=[(t,name,value)]
        # Update result status
        self.set_result(service,result,message)
    ##
    ## Set probe's result for a given services.
    ## Can be called several time, offering error escalation
    ##
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
    ##
    ## Called by subclass when all checks are completed
    ## closing check round
    ##
    def exit(self):
        self.debug("Exit")
        self.next_run=self.start_time+self.interval
        self.start_time=None
        data=[]
        for v in self.pm_data.values():
            data+=v
        self.daemon.exit_probe(self,self.pm_result.values(),data)
    ##
    ## Does probe in checking or idle
    ##
    def _is_active(self):
        return self.start_time is not None
    is_active=property(_is_active)
    ##
    ## Does probe exceed its timeout
    ##
    def _is_stale(self):
        return self.start_time+self.interval<time.time()
    is_stale=property(_is_stale)
    ##
    ## Does probe ready to run
    ##
    def _ready_to_run(self):
        return self.next_run<time.time()
    ready_to_run=property(_ready_to_run)
    ##
    ## Called on each check round.
    ## Must be overriden to provide specific functionality
    ##
    def on_start(self):
        pass
    ##
    ## Called when probe timeout expired.
    ## Must close all running checks. Overriden in subclasses to provide specific functionality
    ##
    def on_stop(self):
        pass
    ## Does configuration section has option 'name'
    def has_option(self,name):
        return self.config.has_option(self.probe_name,name)
    ##
    def __get(self,f,name,default=None):
        try:
            return f(self.probe_name,name)
        except:
            return default
    ## Return 'name' option of configuration section
    def get(self,name,default=None):
        return self.__get(self.config.get,name,default)
    # Return 'name' option of configuration section as integer
    def getint(self,name,default=None):
        return self.__get(self.config.getint,name,default)
    # Return 'name' option of configuration section as float
    def getfloat(self,name,default=None):
        return self.__get(self.config.getfloat,name,default)
    # Format log message
    def __logformat(self,msg):
        return "[%s/%s] %s"%(self.name,self.probe_name,msg)
    # Log 'info' message
    def info(self,msg):
        logging.info(self.__logformat(msg))
    # Log 'error' message
    def error(self,msg):
        logging.error(self.__logformat(msg))
    # Log 'debug' message
    def debug(self,msg):
        logging.debug(self.__logformat(msg))
