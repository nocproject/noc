# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-probe daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.daemon import Daemon
from noc.lib.nbsocket import SocketFactory
from noc.lib.pmhash import pmhash
from noc.pm.probes import probe_registry
from noc.sa.protocols.pm_pb2 import *
import logging,time,bisect,random,socket,time

probe_registry.register_all()

##
## SLA Monitor Daemon
##
class Probe(Daemon):
    daemon_name="noc-probe"
    ##
    ##
    ##
    def __init__(self):
        super(Probe,self).__init__()
        logging.info("Running Probe")
        self.factory=SocketFactory(tick_callback=self.tick)
        self.task_schedule=[]   # Sorted array of probes
        self.active_tasks=set() # Probe names
        self.pm_data_queue=[]
        self.pm_result_queue=[]
        self.init_probes()
        self.collector_host=self.config.get("activator","host")
        self.collector_port=self.config.getint("activator","port")
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.secret=self.config.get("activator","secret")
        self.next_heartbeat=None
    ##
    ## Create probes from config file
    ##
    def init_probes(self):
        for probe_name in self.config.sections():
            if probe_name in ["main","activator","path"]:
                continue
            probe=self.config.get(probe_name,"probe")
            if not probe:
                logging.error("No probe type specified for '%s'"%probe_name)
                continue
            if probe not in probe_registry.classes:
                logging.error("Invalid probe type '%s' for probe '%s'"%(probe,probe_name))
                continue
            probe=probe_registry[probe](self,probe_name,self.config)
            bisect.insort(self.task_schedule,probe)
    ##
    ## Main loop
    ##
    def run(self):
        self.factory.run(run_forever=True)
    ##
    ## Called by factory every second
    ##
    def tick(self):
        # Stop stale tasks
        for t in [t for t in self.active_tasks if t.is_stale]:
            t.stop()
        # Start scheduled task
        while self.task_schedule:
            if self.task_schedule[0].ready_to_run:
                probe=self.task_schedule.pop(0)
                self.active_tasks.add(probe)
                probe.start()
            else:
                break
        # Send collected data
        if self.pm_data_queue or self.pm_result_queue:
            self.send_data()
        # Heartbeat
        t=time.time()
        if self.heartbeat_enable and (self.next_heartbeat is None or self.next_heartbeat<=t):
            self.heartbeat()
            self.next_heartbeat=t+3
    ##
    ## Register probe results
    ##
    def exit_probe(self,probe,pm_result,pm_data):
        self.active_tasks.remove(probe)
        bisect.insort(self.task_schedule,probe)
        self.pm_data_queue+=pm_data
        self.pm_result_queue+=pm_result
    ##
    ## Send collected data and results to the activator
    ##
    def send_data(self):
        MSG_LIMIT=700 # <!> TODO: Remove hardcoded limit
        while self.pm_result_queue or self.pm_data_queue:
            msg=PMMessage()
            # Add random timestamp to toss out hash
            d=msg.result.add()
            d.probe_name=""
            d.probe_type=""
            t=random.randint(0,0x7FFFFFFF)
            d.timestamp=t
            d.service=""
            d.result=0
            d.message=""
            # Pack data
            tses=[t]
            while (self.pm_result_queue or self.pm_data_queue) and msg.ByteSize()<MSG_LIMIT:
                if self.pm_result_queue:
                    result=self.pm_result_queue.pop(0)
                    r=msg.result.add()
                    result.fill_pmresult(r)
                    tses+=[r.timestamp]
                    continue
                if self.pm_data_queue:
                    timestamp,name,value=self.pm_data_queue.pop(0)
                    timestamp=int(timestamp)
                    d=msg.data.add()
                    d.name=name
                    d.timestamp=timestamp
                    if value is None:
                        d.value=0
                        d.is_null=True
                    else:
                        d.value=value
                        d.is_null=False
                    tses+=[timestamp]
                    continue
            # Calculate crypto hash
            msg.checksum=pmhash("127.0.0.1",self.secret,tses)
            print msg
            self.socket.sendto(msg.SerializeToString(),(self.collector_host,self.collector_port))
    