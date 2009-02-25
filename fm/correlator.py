# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.lib.daemon import Daemon
from noc.fm.models import Event,EventCorrelationRule
from noc.lib.fileutils import rewrite_when_differ
from pyke import knowledge_engine
import logging,time,os

class Correlator(Daemon):
    daemon_name="noc-correlator"
    def __init__(self):
        Daemon.__init__(self)
        logging.info("Running Correlator")
    ##
    ## Compile and build rule base
    ##
    def build_rulebase(self):
        s=[]
        for r in EventCorrelationRule.objects.order_by("name"):
            s.append(r.pyke_code)
        c=["local","fm","rules","correlation"]
        d=os.path.join(*c)
        try:
            os.makedirs(d)
        except:
            pass
        # Write krb
        rewrite_when_differ(os.path.join(d,"kb.krb"),"\n".join(s))
        # Write modules __init__.py files when necessary
        for i in range(len(c)):
            path=os.path.join(*c[:i+1]+["__init__.py"])
            if not os.path.exists(path):
                open(path,"w").close()
    
    ##
    ## Populate knowledge base with facts
    ##
    def load_window(self):
        r=[]
        self.ke.reset()
        # Load event window.
        # Populate knowledge base by facts
        for e in Event.objects.order_by("-timestamp")[:1000]:
            en=e.id
            self.ke.assert_("fm","event_class",(en,str(e.event_class.name)))
            self.ke.assert_("fm","managed_object",(en,str(e.managed_object.name)))
            self.ke.assert_("fm","timestamp",(en,int(time.mktime(e.timestamp.timetuple()))))
            for v in e.eventdata_set.filter(type="V"):
                self.ke.assert_("fm","var",(en,str(v.key),str(v.value)))
            r.append(e)
        # Activate rulebase again
        self.ke.activate("kb")
        return r
    ##
    ## Search possible solutions for rule(event,$x)
    ##
    def search(self,rule,event):
        with self.ke.prove_n("kb",rule,(event,),1) as gen:
            for ans in gen:
                yield ans[0][0]
    ##
    ##
    ##
    def process_event(self,e):
        event_id=e.id
        # close(event_id,$x) means $x is closed by event_id
        for ans in self.search("close",event_id):
            logging.debug("Event %d closes event %s"%(event_id,ans))
    ##
    ## main daemon loop
    ##
    def run(self):
        self.build_rulebase()
        self.ke=knowledge_engine.engine("noc.local.fm.rules.correlation")
        #for r in self.ke.get_rb("kb").rules.keys():
        #    self.ke.trace("kb",r)
        events=self.load_window()
        #self.ke.get_kb("fm").dump_specific_facts()
        t0=time.time()
        for e in events:
            self.process_event(e)
        dt=time.time()-t0
        ne=len(events)
        if dt>0:
            p=ne/dt
        else:
            p=len(events)
        logging.debug("%d events processed in %8.2f seconds (%8.2f events/sec)"%(ne,dt,p))
        self.ke.print_stats()
