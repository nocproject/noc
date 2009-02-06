# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.daemon import Daemon
from noc.fm.models import EventClassificationRule,Event,EventData,EventClass,MIB,EventClassVar,EventRepeat
from django.db import transaction
import re,logging,time,datetime

rx_template=re.compile(r"\{\{([^}]+)\}\}")
rx_oid=re.compile(r"^(\d+\.){6,}")

class Rule(object):
    def __init__(self,rule):
        self.rule=rule
        self.name=rule.name
        self.re=[(re.compile(x.left_re),re.compile(x.right_re,re.MULTILINE|re.DOTALL)) for x in rule.eventclassificationre_set.all()]
        
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
                vars.update(l_match.groupdict())
                vars.update(r_match.groupdict())
                break
            if not found:
                return None
        return vars
    
    def _drop_event(self):
        return self.rule.drop_event
    drop_event=property(_drop_event)

class Classifier(Daemon):
    daemon_name="noc-classifier"
    def __init__(self):
        self.rules=[]
        Daemon.__init__(self)
        logging.info("Running Classifier")
    
    def load_config(self):
        super(Classifier,self).load_config()
        self.load_rules()
    
    def load_rules(self):
        logging.info("Loading rules")
        self.rules=[Rule(r) for r in EventClassificationRule.objects.order_by("preference")]
        logging.info("%d rules loaded"%len(self.rules))
    
    def expand_template(self,template,vars):
        return rx_template.sub(lambda m:str(vars.get(m.group(1),"{{UNKNOWN VAR}}")),template)
    
    def classify_event(self,event):
        def is_oid(s):
            return rx_oid.search(s) is not None
        def update_var(event,k,v,t):
            try:
                ed=EventData.objects.get(event=event,key=k,type=t)
                ed.value=v
            except EventData.DoesNotExist:
                ed=EventData(event=event,key=k,value=v,type=t)
            ed.save()
        # Extract received event properties
        props=[(x.key,x.value) for x in event.eventdata_set.filter(type=">")]
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
        for r in self.rules:
            vars=r.match(props)
            if vars is None:
                continue
            # Silently drop event when rule is drop rule
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
        vars.update(resolved)
        subject=self.expand_template(event_class.subject_template,vars)
        if len(subject)>255:
            subject=subject[:250]+" ..."
        event.subject=subject
        event.body=self.expand_template(event_class.body_template,vars)
        event.save()
        
    def run(self):
        INTERVAL=10
        last_sleep=time.time()
        transaction.enter_transaction_management()
        while True:
            n=0
            for e in Event.objects.filter(subject__isnull=True).order_by("id"):
                self.classify_event(e)
                transaction.commit()
                n+=1
            if n:
                logging.info("%d events classified"%n)
            t=time.time()
            if t-last_sleep<=INTERVAL:
                time.sleep(INTERVAL-t+last_sleep)
            last_sleep=t
        transaction.leave_transaction_management()
        

