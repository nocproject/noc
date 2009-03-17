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
from noc.fm.models import EventClassificationRule,Event,EventData,EventClass,MIB,EventClassVar,EventRepeat
from django.db import transaction
from django.template import Template, Context
import re,logging,time,datetime

##
## Patterns
##
rx_template=re.compile(r"\{\{([^}]+)\}\}")
rx_oid=re.compile(r"^(\d+\.){6,}")
rx_mac_cisco=re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")
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
                    return None
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
            print repr(s)
            return "%02X:%02X:%02X:%02X:%02X:%02X"%tuple([ord(x) for x in list(s)])
        if rx_mac_cisco.match(s):
            s=s.replace(".","").upper()
            return "%s:%s:%s:%s:%s:%s"%(s[:2],s[2:4],s[4:6],s[6:8],s[8:10],s[10:])
        raise DecodeError
##
## Noc-classifier daemon
##
class Classifier(Daemon):
    daemon_name="noc-classifier"
    def __init__(self):
        self.rules=[]
        self.templates={} # event_class_id -> (body_template,subject_template)
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
    ##
    ## Classify single event:
    ## 1. Resolve OIDs when source is SNMP Trap
    ## 2. Try to find matching rule
    ## 3. Drop event if required by rule
    ## 4. Set event class of the matched rule or DEFAULT
    ## 
    def classify_event(self,cursor,event):
        def is_oid(s):
            return rx_oid.search(s) is not None
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
        rule_id=0
        for r in self.rules:
            # Try to match rule
            vars=r.match(props)
            if vars is None:
                continue
            rule_id=r.rule.id
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
        # Fill event subject and body
        f_vars=dict(props) # f_vars contains all event vars, including original, extracted and resolved
        f_vars.update(vars)
        f_vars.update(resolved)
        subject_template,body_template=self.templates[event_class.id]
        context=Context(f_vars)
        subject=subject_template.render(context)
        if len(subject)>255: # Too long subject must be truncated
            subject=subject[:250]+" ..."
        body=body_template.render(context)
        # Prepare and call update_event_classification stored procedure for bulk event update
        v_args=[]
        for k,v in resolved.items():
            v_args+=["R",k,bin_quote(v)]
        for k,v in vars.items():
            v_args+=["V",k,bin_quote(v)]
        p="SELECT update_event_classification(%s,%s,%s,%s,%s,%s,%s,ARRAY["
        p+=",".join(["ARRAY[%s,%s,%s]"]*(len(v_args)/3))
        p+="])"
        cursor.execute(p,[event.id,rule_id,event_class.id,event_class.category.id,event_class.default_priority.id,subject,body]+v_args)
        cursor.execute("COMMIT")
        # Finally run event class trigger
        event.event_class.run_trigger(event)
        
    def run(self):
        INTERVAL=10
        last_sleep=time.time()
        transaction.enter_transaction_management()
        from django.db import connection
        cursor = connection.cursor()
        while True:
            n=0
            t0=time.time()
            for e in Event.objects.filter(status="U").order_by("id"):
                self.classify_event(cursor,e)
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
        

