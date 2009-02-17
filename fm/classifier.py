# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-classifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.daemon import Daemon
from noc.lib.pyquote import bin_quote,bin_unquote
from noc.fm.models import EventClassificationRule,Event,EventData,EventClass,MIB,EventClassVar,EventRepeat
from django.db import transaction
import re,logging,time,datetime

##
## Patterns
##
rx_template=re.compile(r"\{\{([^}]+)\}\}")
rx_oid=re.compile(r"^(\d+\.){6,}")
##
## Exceptions
##
class DecodeError(Exception): pass
##
## In-memory Rule representation
##
class Rule(object):
    def __init__(self,rule):
        self.rule=rule
        self.name=rule.name
        self.re=[(re.compile(x.left_re,re.MULTILINE|re.DOTALL),re.compile(x.right_re,re.MULTILINE|re.DOTALL)) for x in rule.eventclassificationre_set.all()]
    ##
    ## Return a hash of extracted variables for object o, or None
    ##
    def match(self,o):
        vars={}
        for l,r in self.re:
            found=False
            for o_l,o_r in o:
                l_match=l.search(o_l)
                if not l_match:
                    continue
                r_match=r.search(o_r)
                if not r_match:
                    continue
                found=True
                # Apply decoders if necessary
                # Decoders are given as (?P<name__decoder>.....) patters
                try:
                    for gd in [l_match.groupdict(),r_match.groupdict()]:
                        for k,v in gd.items():
                            if "__" in k:
                                k_name,decoder=k.split("__",1)
                                vars[k_name]=getattr(self,"decode_%s"%decoder)(v) # Apply decoder
                            else:
                                vars[k]=v # Pass unchanged
                except DecodeError:
                    return None # No match when decoder failed
                except AttributeError:
                    return None # No match when decoder not found
                break
            if not found:
                return None
        return vars
    ## Rule is drop rule
    def _drop_event(self):
        return self.rule.drop_event
    drop_event=property(_drop_event)
    ##
    ## 
    ##
    def decode_ipv4(self,s):
        if len(s)!=4:
            raise DecodeError
        return ".".join(["%d"%ord(c) for c in list(s)])
        
##
## Noc-classifier daemon
##
class Classifier(Daemon):
    daemon_name="noc-classifier"
    def __init__(self):
        self.rules=[]
        Daemon.__init__(self)
        logging.info("Running Classifier")
    ##
    ## Load rules from database after loading config
    ##
    def load_config(self):
        super(Classifier,self).load_config()
        self.load_rules()
    ##
    ## Load rules from database
    ##
    def load_rules(self):
        logging.info("Loading rules")
        self.rules=[Rule(r) for r in EventClassificationRule.objects.order_by("preference")]
        logging.info("%d rules loaded"%len(self.rules))
    ##
    ## Replace all variable occurences in template by variables content
    ##
    def expand_template(self,template,vars):
        return rx_template.sub(lambda m:str(vars.get(m.group(1),"{{UNKNOWN VAR}}")),template)
    ##
    ## Classify single event:
    ## 1. Resolve OIDs when source is SNMP Trap
    ## 2. Try to find matching rule
    ## 3. Drop event if required by rule
    ## 4. Set event class of the matched rule or DEFAULT
    ## 
    def classify_event(self,event):
        def is_oid(s):
            return rx_oid.search(s) is not None
        # Save event's variables
        def update_var(event,k,v,t):
            v=bin_quote(v)
            try:
                ed=EventData.objects.get(event=event,key=k,type=t)
                ed.value=v
            except EventData.DoesNotExist:
                ed=EventData(event=event,key=k,value=v,type=t)
            ed.save()
        # Extract received event properties
        props=[(x.key,bin_unquote(x.value)) for x in event.eventdata_set.filter(type=">")]
        # Resolve additional event properties
        source=None
        for k,v in props:
            if k=="source":
                source=v
                break
        resolved={
            "profile":event.managed_object.profile_name
        }
        # Resolve SNMP oids
        if source=="SNMP Trap":
            for k,v in props:
                if is_oid(k):
                    oid=MIB.get_name(k)
                    if oid!=k:
                        if is_oid(v):
                            v=MIB.get_name(v)
                        resolved[oid]=v
        if resolved:
            props+=resolved.items()
        # Find rule
        event_class=None
        # Try to find matching rule
        for r in self.rules:
            # Try to match rule
            vars=r.match(props)
            if vars is None:
                continue
            # Silently drop event when required by rule
            if r.drop_event:
                logging.debug("Drop event %d"%event.id)
                [ed.delete() for ed in event.eventdata_set.all()]
                event.delete()
                return
            event_class=r.rule.event_class
            logging.debug("Matching class for event %d found: %s (Rule: %s)"%(event.id,event_class.name,r.name))
            # Check the event is repeatition of existing one
            if event_class.repeat_suppression and event_class.repeat_suppression_interval>0:
                # Delete event as repeatition of the known event
                # Build keys
                kv={}
                for name in [v.name for v in EventClassVar.objects.filter(event_class=event_class,repeat_suppression=True)]:
                    if name in vars:
                        kv[name]=vars[name]
                    else:
                        kv=None
                        break
                if kv is not None:
                    r=[e for e in Event.objects.filter(
                        event_class=event_class,
                        managed_object=event.managed_object,
                        timestamp__gte=event.timestamp-datetime.timedelta(seconds=event_class.repeat_suppression_interval),
                        timestamp__lte=event.timestamp
                        ).exclude(id=event.id).order_by("-timestamp")
                        if e.match_data(kv)]
                    if len(r)>0:
                        pe=r[0]
                        logging.debug("Event #%d repeats event #%d"%(event.id,pe.id))
                        er=EventRepeat(event=pe,timestamp=pe.timestamp)
                        er.save()
                        pe.timestamp=event.timestamp
                        pe.save()
                        [ed.delete() for ed in event.eventdata_set.all()]
                        event.delete()
                        return
            break
        # Set event class to DEFAULT when no matching rule found
        if event_class is None:
            event_class=EventClass.objects.get(name="DEFAULT")
            vars={}
            logging.debug("No rule found for event %d. Falling back to DEFAULT"%event.id)
        # Do additional processing
        # Clean up enriched data
        [d.delete() for d in  event.eventdata_set.filter(type__in=["R","V"])]
        # Enrich event by extracted variables
        for k,v in vars.items():
            update_var(event,k,v,"V")
        # Enrich event by resolved variables
        for k,v in resolved.items():
            update_var(event,k,v,"R")
        # Set up event class, category and priority
        event.event_class=event_class
        event.event_category=event_class.category
        event.event_priority=event_class.default_priority
        # Fill event subject and body
        f_vars=dict(props) # f_vars contains all event vars, including original, extracted and resolved
        f_vars.update(vars)
        f_vars.update(resolved)
        subject=self.expand_template(event_class.subject_template,f_vars)
        if len(subject)>255: # Too long subject must be truncated
            subject=subject[:250]+" ..."
        event.subject=subject
        event.body=self.expand_template(event_class.body_template,f_vars)
        event.save()
        # Finally run event class trigger
        event.event_class.run_trigger(event)
        
    def run(self):
        INTERVAL=10
        last_sleep=time.time()
        transaction.enter_transaction_management()
        while True:
            n=0
            t0=time.time()
            for e in Event.objects.filter(subject__isnull=True).order_by("id"):
                self.classify_event(e)
                transaction.commit()
                n+=1
            if n:
                dt=time.time()-t0
                if dt>0:
                    perf=n/dt
                else:
                    perf=0
                logging.info("%d events classified (%10.4f second elapsed. %10.4f events/sec)"%(n,dt,perf))
            t=time.time()
            if t-last_sleep<=INTERVAL:
                time.sleep(INTERVAL-t+last_sleep)
            last_sleep=t
        transaction.leave_transaction_management()
        

