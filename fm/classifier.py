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
from noc.lib.validators import is_ipv4
from noc.fm.models import EventClassificationRule,Event,EventData,EventClass,MIB,EventClassVar,EventRepeat,EventPostProcessingRule
from django.db import transaction,reset_queries
from django.template import Template, Context
import re,logging,time,datetime

##
## Patterns
##
rx_template=re.compile(r"\{\{([^}]+)\}\}")
rx_oid=re.compile(r"^(\d+\.){6,}")
rx_mac_cisco=re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")
##
## Global functions for variables evaluation
##

##
## Decode IPv4 from 4 octets
##
def decode_ipv4(s):
    if len(s)==4:
        return ".".join(["%d"%ord(c) for c in list(s)])
    if is_ipv4(s):
        return s
    raise DecodeError
##
## Decode MAC address from 6 octets
##
def decode_mac(s):
    if len(s)==6:
        return "%02X:%02X:%02X:%02X:%02X:%02X"%tuple([ord(x) for x in list(s)])
    if rx_mac_cisco.match(s):
        s=s.replace(".","").upper()
        return "%s:%s:%s:%s:%s:%s"%(s[:2],s[2:4],s[4:6],s[6:8],s[8:10],s[10:])
    raise DecodeError
##
## Global variables dict
##
eval_globals={
    "decode_ipv4" : decode_ipv4,
    "decode_mac"  : decode_mac,
}

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
        self.re=[(re.compile(x.left_re,re.MULTILINE|re.DOTALL),re.compile(x.right_re,re.MULTILINE|re.DOTALL)) for x in rule.eventclassificationre_set.filter(is_expression=False)]
        self.expressions=[(x.left_re,compile(x.right_re,"inline","eval")) for x in rule.eventclassificationre_set.filter(is_expression=True)]
        if not self.expressions:
            self.expressions=None
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
                    return None
                found=True
                vars.update(l_match.groupdict()) # Populate vars with extracted variables
                vars.update(r_match.groupdict())
                break
            if not found:
                return None
        return vars
    ##
    ## Decode IPv4 from 4 octets
    ##
    def decode_ipv4(self,s):
        if len(s)==4:
            return ".".join(["%d"%ord(c) for c in list(s)])
        if is_ipv4(s):
            return s
        raise DecodeError
    ##
    ## Decode MAC address from 6 octets
    ##
    def decode_mac(self,s):
        if len(s)==6:
            return "%02X:%02X:%02X:%02X:%02X:%02X"%tuple([ord(x) for x in list(s)])
        if rx_mac_cisco.match(s):
            s=s.replace(".","").upper()
            return "%s:%s:%s:%s:%s:%s"%(s[:2],s[2:4],s[4:6],s[6:8],s[8:10],s[10:])
        raise DecodeError
##
## Post-Process rule
##
class PostProcessRule(object):
    def __init__(self,rule):
        self.rule=rule
        self.name=rule.name
        self.re=[(re.compile(x.var_re,re.MULTILINE|re.DOTALL),re.compile(x.value_re,re.MULTILINE|re.DOTALL)) for x in rule.eventpostprocessingre_set.all()]
    
    def match(self,vars):
        v=vars.items()
        for rx_var,rx_value in self.re:
            matched=False
            for var,value in v:
                if rx_var.match(var) and rx_value.match(value):
                    matched=True
                    break
            if not matched:
                return False
        return True

##
## Noc-classifier daemon
##
class Classifier(Daemon):
    daemon_name="noc-classifier"
    def __init__(self):
        self.rules=[]
        self.templates={} # event_class_id -> (body_template,subject_template)
        self.post_process={} # event_class_id -> [rule1, ..., ruleN]
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
        logging.info("%d rules are loaded"%len(self.rules))
        logging.info("Compiling templates")
        self.templates=dict([(ec.id,(Template(ec.subject_template),Template(ec.body_template))) for ec in EventClass.objects.all()])
        logging.info("%d templates are compiled"%len(self.templates)*2)
        logging.info("Loading post-process rules")
        self.post_process={}
        n=0
        for r in EventPostProcessingRule.objects.order_by("preference"):
            ec_id=r.event_class.id
            if ec_id not in self.post_process:
                self.post_process[ec_id]=[]
            self.post_process[ec_id].append(PostProcessRule(r))
            n+=1
        logging.info("%d post-processing rules are loaded"%n)
    ##
    ## Classify single event:
    ## 1. Resolve OIDs when source is SNMP Trap
    ## 2. Try to find matching rule
    ## 3. Drop event if required by rule
    ## 4. Set event class of the matched rule or DEFAULT
    ## 
    def classify_event(self,event):
        # Extract received event properties
        props=[(x.key,bin_unquote(x.value)) for x in event.eventdata_set.filter(type=">")]
        # Resolve additional event properties
        resolved={
            "profile":event.managed_object.profile_name
        }
        # Resolve SNMP oids
        if self.get_source(props)=="SNMP Trap":
            resolved.update(self.resolve_snmp_oids(props))
        props+=resolved.items()
        # Find rule
        status="A"
        rule,vars=self.find_classification_rule(event,props)
        if rule: # Rule found
            if rule.rule.action=="D": # Drop event when required by rule
                self.drop_event(event)
                return
            event_class=rule.rule.event_class
            event.event_class=event_class
            if event_class.repeat_suppression and event_class.repeat_suppression_interval>0 and self.suppress_repeat(event,vars):
                return # Event is suppressed, no further processing
            event_category=event_class.category
            event_priority=event_class.default_priority
            # Find post-processing rule
            post_process=self.find_post_processing_rule(event,vars)
            if post_process:
                # Notify if necessary
                if post_process.rule.notification_group:
                    post_process.rule.notification_group.notify(subject=event.subject,body=event.body)
                if post_process.rule.action=="D": # Drop event if required by post_process_rule
                    self.drop_event(event)
                    return
                if post_process.rule.change_category:
                    event_category=post_process.rule.change_category # Set up priority and category from rule
                if post_process.rule.change_priority:
                    event_priority=post_process.rule.change_priority
                status=post_process.rule.action
            event.log("CLASSIFICATION RULE: %s"%rule.name,to_status=status)
            if post_process:
                event.log("POST-PROCESS RULE: %s"%post_process.name,from_status=status,to_status=status)
        else:
            # Set event class to DEFAULT when no matching rule found
            event_class=EventClass.objects.get(name="DEFAULT")
            vars={}
            logging.debug("No rule found for event %d. Falling back to DEFAULT"%event.id)
            event_category=event_class.category
            event_priority=event_class.default_priority
            event.log("FALLBACK TO DEFAULT")
        # Fill event subject and body
        f_vars=dict(props) # f_vars contains all event vars, including original, extracted and resolved
        f_vars.update(vars)
        f_vars.update(resolved)
        # Does rule contain additional expressions which are need to be calculated?
        if rule and rule.expressions:
            c_vars=dict([(x[0],str(eval(x[1],f_vars,eval_globals))) for x in rule.expressions]) # Evaluate all expressions
            f_vars.update(c_vars) # Update var dicts
            vars.update(c_vars)
        subject_template,body_template=self.templates[event_class.id]
        context=Context(f_vars)
        subject=subject_template.render(context)
        if len(subject)>255: # Too long subject must be truncated
            subject=subject[:250]+" ..."
        body=body_template.render(context)
        # Set up event
        event.event_class=event_class
        event.event_category=event_category
        event.event_priority=event_priority
        event.status=status
        event.subject=subject
        event.body=body
        event.save()
        # Write event vars
        event.eventdata_set.filter(type__in=["R","V"]).delete() # Delete old "R" and "V" vars
        # Write vars
        for k,v in resolved.items():
            EventData(event=event,key=k,value=bin_quote(v),type="R").save()
        for k,v in vars.items():
            EventData(event=event,key=k,value=bin_quote(v),type="V").save()
        # Finally run event class trigger
        event.event_class.run_trigger(event)
    ##
    ## Return event source
    ##
    def get_source(self,props):
        for k,v in props:
            if k=="source":
                return v
        return None
    ##
    ## Resolve SNMP oids to symbolic names
    ##
    def resolve_snmp_oids(self,props):
        def is_oid(s):
            return rx_oid.search(s) is not None
        resolved={}
        for k,v in props:
            if is_oid(k):
                oid=MIB.get_name(k)
                if oid!=k:
                    if is_oid(v):
                        v=MIB.get_name(v)
                    resolved[oid]=v
        return resolved
        
    ##
    ## Find classification rule.
    ## Returns Rule,vars or None,None
    ##
    def find_classification_rule(self,event,props):
        for r in self.rules:
            # Try to match rule
            vars=r.match(props)
            if vars is not None:
                logging.debug("Matching class for event %d found: %s (Rule: %s)"%(event.id,r.rule.event_class.name,r.name))
                return r,vars
        return None,None
        
    ##
    ## Find matching postprocessing rule for event class.
    ## Returns PostProcessRule or None
    ##
    def find_post_processing_rule(self,event,vars):
        event_class=event.event_class
        if event_class.id in self.post_process:
            for r in self.post_process[event_class.id]:
                # Check time pattern
                if r.rule.time_pattern and not r.rule.time_pattern.match(event.timestamp):
                    continue
                # Check object selector
                if r.rule.managed_object_selector and not r.rule.managed_object_selector.match(event.managed_object):
                    continue
                # Check vars
                if r.match(vars):
                    logging.debug("Event #%d matches post-processing rule '%s'"%(event.id,r.name))
                    return r
        return None
    ##
    ## Drop event
    ##
    def drop_event(self,event):
        logging.debug("Drop event #%d"%event.id)
        event.delete()
    ##
    ## Suppress repeats.
    ## Return True if event is suppressed, False otherwise
    ##
    def suppress_repeat(self,event,vars):
        event_class=event.event_class
        # Build keys
        kv={}
        for name in [v.name for v in EventClassVar.objects.filter(event_class=event_class,repeat_suppression=True)]:
            if name in vars:
                kv[name]=vars[name]
            else:
                return False
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
            event.delete()
            return True
    ##
    ## Main daemon loop
    ##
    def run(self):
        CHUNK=1000 # Maximum amount of events to proceed at once
        INTERVAL=10
        transaction.enter_transaction_management()
        while True:
            n=0
            t0=time.time()
            for e in Event.objects.filter(status="U").order_by("-id")[:CHUNK]:
                self.classify_event(e)
                transaction.commit()
                reset_queries() # Free queries log
                n+=1
            if n: # Write out performance data
                dt=time.time()-t0
                if dt>0:
                    perf=n/dt
                else:
                    perf=0
                logging.info("%d events classified (%10.4f second elapsed. %10.4f events/sec)"%(n,dt,perf))
            else: # No events classified this pass. Sleep
                time.sleep(INTERVAL)
        transaction.leave_transaction_management()
        

