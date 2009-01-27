from noc.lib.daemon import Daemon
from noc.fm.models import EventClassificationRule,Event,EventData,EventClass
import re,logging,time

rx_template=re.compile(r"\{\{([^}]+)\}\}")

class Rule(object):
    def __init__(self,rule):
        self.rule=rule
        self.re=[(re.compile(x.left_re),re.compile(x.right_re)) for x in rule.eventclassificationre_set.all()]
        
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
        # Extract event properties
        props=[(x.key,x.value) for x in event.eventdata_set.filter(is_enriched=False)]
        # Find rule
        event_class=None
        for r in self.rules:
            vars=r.match(props)
            if vars is not None:
                event_class=r.rule.event_class
                break
        if event_class is None:
            event_class=EventClass.objects.get(name="DEFAULT")
            vars={}
        # Do additional processing
        # Clean up enriched data
        [d.delete() for d in  event.eventdata_set.filter(is_enriched=True)]
        # Enrich event by extracted variables
        for k,v in vars.items():
            ed=EventData(event=event,key=k,value=v,is_enriched=True)
            ed.save()
        # Set up event class, category and priority
        event.event_class=event_class
        event.event_category=event_class.category
        event.priority=event_class.default_priority
        # Fill event subject and body
        event.subject=self.expand_template(event_class.subject_template,vars)
        event.body=self.expand_template(event_class.body_template,vars)
        event.save()
        
    def run(self):
        while True:
            n=0
            for e in Event.objects.filter(subject__isnull=True):
                self.classify_event(e)
                n+=1
            if n:
                logging.info("%d events classified"%n)
            time.sleep(10)

