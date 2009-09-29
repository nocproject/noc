# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.db import models
from noc.sa.models import ManagedObject,ManagedObjectSelector
from noc.main.models import TimePattern,NotificationGroup
from noc.settings import config
from noc.lib.fileutils import safe_rewrite
from noc.fm.triggers import event_trigger_registry
from noc.main.menu import Menu
import imp,subprocess,tempfile,os,datetime,re

##
event_trigger_registry.register_all()
##
## Python quote helper
##
def py_q(s):
    return s.replace("\"","\\\"")

##
## Exceptions
##
class MIBRequiredException(Exception):
    def __init__(self,mib,requires_mib):
        super(MIBRequiredException,self).__init__()
        self.mib=mib
        self.requires_mib=requires_mib
    def __str__(self):
        return "%s requires %s"%(self.mib,self.requires_mib)
##
class MIBNotFoundException(Exception):
    def __init__(self,mib):
        super(MIBNotFoundException,self).__init__()
        self.mib=mib
    def __str__(self):
        return "MIB not found: %s"%self.mib


##
## Regular expressions
##
rx_module_not_found=re.compile(r"{module-not-found}.*`([^']+)'")
rx_py_id=re.compile("[^0-9a-zA-Z]+")
rx_mibentry=re.compile(r"^((\d+\.){5,}\d+)|(\S+::\S+)$")
rx_mib_name=re.compile(r"^(\S+::\S+?)(.\d+)?$")

##
## SNMP MIB
##
class MIB(models.Model):
    class Meta:
        verbose_name="MIB"
        verbose_name_plural="MIBs"
        ordering=["name"]
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",blank=True,null=True)
    last_updated=models.DateTimeField("Last Updated") # Latest revision of MIB
    uploaded=models.DateTimeField("Uploaded")
    
    def __unicode__(self):
        return self.name
    ##
    ## Load MIB into database
    ## smidump from libsmi used to parse MIB
    ##
    @classmethod
    def load(self,path):
        # Build SMIPATH variable for smidump to exclude locally installed MIBs
        smipath=["share/mibs","local/share/mibs"]
        # Pass MIB through smilint to detect missed modules
        f=subprocess.Popen([config.get("path","smilint"),"-m",path],stderr=subprocess.PIPE,env={"SMIPATH":":".join(smipath)}).stderr
        for l in f:
            match=rx_module_not_found.search(l.strip())
            if match:
                raise MIBRequiredException("Uploaded MIB",match.group(1))
        # Convert MIB to python module and load
        h,p=tempfile.mkstemp()
        subprocess.check_call([config.get("path","smidump"),"-k","-f","python","-o",p,path],
            env={"SMIPATH":":".join(smipath)})
        m=imp.load_source("mib",p)
        os.close(h)
        os.unlink(p)
        mib_name=m.MIB["moduleName"]
        # Check module dependencies
        depends_on={}
        if "imports" in m.MIB:
            for i in m.MIB["imports"]:
                if "module" not in i:
                    continue
                rm=i["module"]
                if rm in depends_on:
                    continue
                try:
                    depends_on[rm]=MIB.objects.get(name=rm)
                except MIB.DoesNotExist:
                    raise MIBRequiredException(mib_name,rm)
        # Get MIB latest revision date
        try:
            last_updated=datetime.datetime.strptime(sorted([x["date"] for x in m.MIB[mib_name]["revisions"]])[-1],"%Y-%m-%d %H:%M")
        except:
            last_updated=datetime.datetime(year=1970,month=1,day=1)
        # Check mib already uploaded
        mib_description=m.MIB[mib_name].get("description",None)
        try:
            mib=MIB.objects.get(name=mib_name)
            # Skip same version
            if mib.last_updated>=last_updated:
                return mib
            mib.description=mib_description
            mib.uploaded=datetime.datetime.now()
            mib.last_updated=last_updated
            mib.save()
            # Delete all MIB Data
            [d.delete() for d in mib.mibdata_set.all()]
        except MIB.DoesNotExist:
            o=None
            mib=MIB(name=mib_name,description=mib_description,uploaded=datetime.datetime.now(),last_updated=last_updated)
            mib.save()
        # Save MIB Data
        for i in ["nodes","notifications"]:
            if i in m.MIB:
                for node,v in m.MIB[i].items():
                    try: # Do not import duplicated OIDs
                        MIBData.objects.get(oid=v["oid"])
                    except MIBData.DoesNotExist:
                        d=MIBData(mib=mib,oid=v["oid"],name="%s::%s"%(mib_name,node),description=v.get("description",None))
                        d.save()
        # Save MIB Dependency
        for r in depends_on.values():
            md=MIBDependency(mib=mib,requires_mib=r)
            md.save()
        # Save MIB to cache if not uploaded from cache
        lcd=os.path.join("local","share","mibs")
        if not os.path.isdir(lcd): # Ensure directory exists
            os.makedirs(os.path.join("local","share","mibs")) 
        local_cache_path=os.path.join(lcd,"%s.mib"%mib_name)
        cache_path=os.path.join("share","mibs","%s.mib"%mib_name)
        if (os.path.exists(local_cache_path) and os.path.samefile(path,local_cache_path))\
            or (os.path.exists(cache_path) and os.path.samefile(path,cache_path)):
            return mib
        with open(path) as f:
            data=f.read()
        safe_rewrite(local_cache_path,data)
        return mib
    ##
    ## Get OID by name
    ##
    @classmethod
    def get_oid(cls,name):
        try:
            o=MIBData.objects.get(name=name)
            return o.oid
        except MIBData.DoesNotExist:
            return None
    ##
    ## Get longest matched name by oid
    ##
    @classmethod
    def get_name(cls,oid):
        l_oid=oid.split(".")
        rest=[]
        while l_oid:
            c_oid=".".join(l_oid)
            try:
                o=MIBData.objects.get(oid=c_oid)
                name=o.name
                if rest:
                    name+="."+".".join(reversed(rest))
                return name
            except MIBData.DoesNotExist:
                rest.append(l_oid.pop())
        return oid
    ##
    ## Returns description for symbolic/OID string
    ##
    @classmethod
    def get_description(self,v):
        if not rx_mibentry.match(v):
            return ""
        if "::" in v:
            # MIB::name
            match=rx_mib_name.match(v)
            if not match:
                return ""
            try:
                d=MIBData.objects.get(name=match.group(1))
                return d.description
            except MIBData.DoesNotExist:
                return ""
        else:
            # Pure OID
            try:
                d=MIBData.objects.get(oid=v)
                return d.description
            except MIBData.DoesNotExist:
                pass
            try:
                d=MIBData.objects.get(oid=".".join((v.split(".")[:-1])))
                return d.description
            except MIBData.DoesNotExist:
                return ""
            
##
## MIB elements
##
class MIBData(models.Model):
    class Meta:
        verbose_name="MIB Data"
        verbose_name_plural="MIB Data"
        ordering=["oid"]
    mib = models.ForeignKey(MIB,verbose_name="MIB")
    oid = models.CharField("OID",max_length=128,unique=True)
    name= models.CharField("Name",max_length=128,unique=True)
    description= models.TextField("Description",blank=True,null=True)

    def __unicode__(self):
        return "%s:%s = %s"%(self.mib.name,self.name,self.oid)
##
## MIB Dependency
##
class MIBDependency(models.Model):
    class Meta:
        verbose_name="MIB Import"
        verbose_name_plural="MIB Imports"
        unique_together=[("mib","requires_mib")]
    mib=models.ForeignKey(MIB,verbose_name="MIB")
    requires_mib=models.ForeignKey(MIB,verbose_name="Requires MIB",related_name="requiredbymib_set")
    
    def __unicode__(self):
        return "%s requires %s"%(self.mib.name,self.requires_mib.name)
    ##
    ## Return graphviz dot with MIB dependencies
    ##
    @classmethod
    def get_dot(cls):
        r=["digraph {"]
        r+=["label=\"MIB Dependencies\";"]
        for d in cls.objects.all():
            r+=["\"%s\" -> \"%s\";"%(d.mib.name,d.requires_mib.name)]
        r+=["}"]
        return "\n".join(r)
    ##
    ## Write graphviz dot with MIB dependencies
    ##
    @classmethod
    def write_dot(cls,path):
        safe_rewrite(path,cls.get_dot())
##
## Events
##
class EventPriority(models.Model):
    class Meta:
        verbose_name="Event Priority"
        verbose_name_plural="Event Priorities"
        ordering=["priority"]
    name=models.CharField("Name",max_length=32,unique=True)
    priority=models.IntegerField("Priority")
    description=models.TextField("Description",blank=True,null=True)
    font_color=models.CharField("Font Color",max_length=32,blank=True,null=True)
    background_color=models.CharField("Background Color",max_length=32,blank=True,null=True)
    def __unicode__(self):
        return self.name
    def _css_style_name(self):
        return "CSS_%s"%self.name.replace(" ","")
    css_style_name=property(_css_style_name)
    def _css_style(self):
        s=[]
        if self.font_color:
            s+=["    color: %s;"%self.font_color]
        if self.background_color:
            s+=["    background: %s;"%self.background_color]
        return ".%s {\n%s\n}"%(self.css_style_name,"\n".join(s))
    css_style=property(_css_style)
##
## Event categories.
## Event categories separate events to area of responsibility (Network event, System event, Security event)
##
class EventCategory(models.Model):
    class Meta:
        verbose_name="Event Category"
        verbose_name_plural="Event Categories"
        ordering=["name"]
    name=models.CharField("Name",max_length=32,unique=True)
    description=models.TextField("Description",blank=True,null=True)

    def __unicode__(self):
        return self.name
##
## Event classes.
## Event class specifies a kind of event with predefined set of event variables.
## Event classes are assigned by Classifier process.
## Correlator process performs event corelation mostly using event class analysys
##
class EventClass(models.Model):
    class Meta:
        verbose_name="Event Class"
        verbose_name_plural="Event Classes"
        ordering=["name"]
    name=models.CharField("Name",max_length=64)
    category=models.ForeignKey(EventCategory,verbose_name="Event Category")
    default_priority=models.ForeignKey(EventPriority,verbose_name="Default Priority")
    subject_template=models.CharField("Subject Template",max_length=128)
    body_template=models.TextField("Body Template")
    last_modified=models.DateTimeField("last_modified",auto_now=True)
    repeat_suppression=models.BooleanField("Repeat Suppression",default=False)
    repeat_suppression_interval=models.IntegerField("Repeat Suppression interval (secs)",default=3600)
    trigger=models.CharField("Trigger",max_length=64,null=True,blank=True,choices=event_trigger_registry.choices)
    is_builtin=models.BooleanField("Is Builtin",default=False)
    
    def __unicode__(self):
        return self.name
    
    def python_link(self):
        return "<A HREF='/fm/py_event_class/%d/'>Python</A>"%self.id
    python_link.short_description="Python"
    python_link.allow_tags=True
    ##
    ## Run trigger if defined
    ##
    def run_trigger(self,event):
        if self.trigger and self.trigger in event_trigger_registry.classes:
            event_trigger_registry.classes[self.trigger]().handle(event)
    ##
    ## Python representation of data structure
    ##
    def _python_code(self):
        s=["##","## %s"%self.name,"##"]
        s+=["class %s(EventClass):"%rx_py_id.sub("",self.name)]
        s+=["    name     = \"%s\""%py_q(self.name)]
        s+=["    category = \"%s\""%py_q(self.category.name)]
        s+=["    priority = \"%s\""%py_q(self.default_priority.name)]
        s+=["    subject_template=\"%s\""%py_q(self.subject_template)]
        s+=["    body_template=\"\"\"%s\"\"\""%self.body_template]
        s+=["    repeat_suppression=%s"%self.repeat_suppression]
        s+=["    repeat_suppression_interval=%d"%self.repeat_suppression_interval]
        if self.trigger:
            s+=["    trigger=\"%s\""%self.trigger]
        else:
            s+=["    trigger=None"]
        vars=list(self.eventclassvar_set.all())
        if vars:
            s+=["    class Vars:"]
            for v in vars:
                s+=["        %s=Var(required=%s,repeat=%s)"%(v.name,v.required,v.repeat_suppression)]
        s+=[]
        return "\n".join(s)
    python_code=property(_python_code)
##
## Event class variables
##
class EventClassVar(models.Model):
    class Meta:
        verbose_name="Event Class Variable"
        verbose_name_plural="Event Class Variables"
        unique_together=[("event_class","name")]
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    name=models.CharField("Name",max_length=64)
    required=models.BooleanField("Required",default=True)
    repeat_suppression=models.BooleanField("Repeat Suppression",default=False) # Used for repeat supression
    def __unicode__(self):
        return "%s: %s"%(self.event_class,self.name)
##
## Classification rule.
## Used by Correlator process for assigning event class to unclassified events
##
class EventClassificationRule(models.Model):
    class Meta:
        verbose_name="Event Classification Rule"
        verbose_name_plural="Event Classification Rules"
        ordering=["preference"]
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    name=models.CharField("Name",max_length=64)
    preference=models.IntegerField("Preference",1000)
    action=models.CharField("Action",max_length=1,choices=[("A","Make Active"),("C","Close"),("D","Drop")],default="A")
    is_builtin=models.BooleanField("Is Builtin",default=False)
    
    def __unicode__(self):
        return self.name
        
    def python_link(self):
        return "<A HREF='/fm/py_event_classification_rule/%d/'>Python</A>"%self.id
    python_link.short_description="Python"
    python_link.allow_tags=True
    ##
    ## Python representation of data structure
    ##
    def _python_code(self):
        s=["from noc.fm.rules.classification import ClassificationRule,Expression,CLOSE_EVENT,DROP_EVENT"]
        s+=["##","## %s"%self.name,"##"]
        s+=["class %s_Rule(ClassificationRule):"%rx_py_id.sub("_",self.name)]
        s+=["    name=\"%s\""%py_q(self.name)]
        s+=["    event_class=%s"%self.event_class.name.replace(" ","").replace("-","_")]
        s+=["    preference=%d"%self.preference]
        if self.action!="A":
            s+=["    action=%s"%{"C":"CLOSE_EVENT","D":"DROP_EVENT"}[self.action]]
        s+=["    patterns=["]
        for p in self.eventclassificationre_set.all():
            if p.is_expression:
                s+=["        Expression(r\"%s\",r\"%s\"),"%(py_q(p.left_re),py_q(p.right_re))]
            else:
                s+=["        (r\"%s\",r\"%s\"),"%(py_q(p.left_re),py_q(p.right_re))]
        s+=["    ]",""]
        return "\n".join(s)
    python_code=property(_python_code)
##
## Regular expressions to match event vars
##
class EventClassificationRE(models.Model):
    class Meta:
        verbose_name="Event Classification RE"
        verbose_name_plural="Event Classification REs"
    rule=models.ForeignKey(EventClassificationRule,verbose_name="Event Classification Rule")
    left_re=models.CharField("Left RE",max_length=256)
    right_re=models.CharField("Right RE",max_length=256)
    is_expression=models.BooleanField("Is Expression",default=False)
    ##
    ## Check expression syntax before save
    ##
    def save(self):
        if self.is_expression:
            compile(self.right_re,"inline","eval") # Raise SyntaxError in case of invalid expression
        super(EventClassificationRE,self).save()
##
## Event Post Processing
##
class EventPostProcessingRule(models.Model):
    class Meta:
        verbose_name="Event Post-Processing Rule"
        verbose_name_plural="Event Post-Processing Rules"
    name=models.CharField("Name",max_length=64)
    preference=models.IntegerField("Preference",default=1000)
    is_active=models.BooleanField("Is Active",default=True)
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    description=models.TextField("Description",blank=True,null=True)
    managed_object_selector=models.ForeignKey(ManagedObjectSelector,verbose_name="Managed Object Selector",null=True,blank=True)
    time_pattern=models.ForeignKey(TimePattern,verbose_name="Time Pattern",null=True,blank=True)
    # Actions
    change_priority=models.ForeignKey(EventPriority,verbose_name="Change Priority to",blank=True,null=True)
    change_category=models.ForeignKey(EventCategory,verbose_name="Change Category to",blank=True,null=True)
    action=models.CharField("Action",max_length=1,choices=[("A","Make Active"),("C","Close"),("D","Drop")],default="A")
    notification_group=models.ForeignKey(NotificationGroup,verbose_name="Notification Group",null=True,blank=True)
    def __unicode__(self):
        return self.name
##
## Regular expressions to match event vars
##
class EventPostProcessingRE(models.Model):
    class Meta:
        verbose_name="Event Post-Processing RE"
        verbose_name_plural="Event Post-Processing REs"
    rule=models.ForeignKey(EventPostProcessingRule,verbose_name="Event Post-Processing Rule")
    var_re=models.CharField("Var RE",max_length=256)
    value_re=models.CharField("Value RE",max_length=256)
##
## Event Correlation Rule
##
class EventCorrelationRule(models.Model):
    class Meta:
        verbose_name="Event Correlation Rule"
        verbose_name_plural="Event Correlation Rules"
        ordering=["name"]
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",null=True,blank=True)
    is_builtin=models.BooleanField("Is Builtin",default=False)
    rule_type=models.CharField("Rule Type",max_length=32,choices=[("Pair","Pair")])
    action=models.CharField("Action",max_length=1,choices=[("C","Close"),("D","Drop"),("P","Root (parent)"),("c","Root (child)")])
    same_object=models.BooleanField("Same Object",default=True)
    window=models.IntegerField("Window (sec)",default=0)

    def __unicode__(self):
        return self.name
        
    def python_link(self):
        return "<A HREF='/fm/py_event_correlation_rule/%d/'>Python</A>"%self.id
    python_link.short_description="Python"
    python_link.allow_tags=True
    ##
    ## Python representation of data structure
    ##
    def _python_code(self):
        s=["from noc.fm.rules.correlation import *"]
        s+=["##","## %s"%self.name,"##"]
        s+=["class %s_Rule(CorrelationRule):"%rx_py_id.sub("_",self.name)]
        s+=["    name=\"%s\""%py_q(self.name)]
        s+=["    description=\"%s\""%py_q(self.description)]
        s+=["    rule_type=\"%s\""%py_q(self.rule_type)]
        s+=["    action=%s"%{"C":"CLOSE_EVENT"}[self.action]]
        s+=["    same_object=%s"%self.same_object]
        s+=["    window=%s"%self.window]
        s+=["    classes=[%s]"%(",".join([rx_py_id.sub("",x.event_class.name) for x in self.eventcorrelationmatchedclass_set.all()]))]
        s+=["    vars=[%s]"%(",".join(["\"%s\""%x.var for x in self.eventcorrelationmatchedvar_set.all()]))]
        return "\n".join(s)
    python_code=property(_python_code)
##
## Matched class list for correlation rule
##
class EventCorrelationMatchedClass(models.Model):
    class Meta:
        verbose_name="Event Correlation Rule Matched Class"
        verbose_name="Event Correlation Rule Matched Classes"
        unique_together=[("rule","event_class")]
    rule=models.ForeignKey(EventCorrelationRule,verbose_name="Rule")
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
##
## Matched var list for correlation rule
##
class EventCorrelationMatchedVar(models.Model):
    class Meta:
        verbose_name="Event Correlation Rule Matched Var"
        verbose_name="Event Correlation Rule Matched Vars"
        unique_together=[("rule","var")]
    rule=models.ForeignKey(EventCorrelationRule,verbose_name="Rule")
    var=models.CharField("Variable Name",max_length=256)
##
## Event itself
##
EVENT_STATUS_CHOICES=[("U","Unclassified"),("A","Active"),("C","Closed")]
class Event(models.Model):
    class Meta:
        verbose_name="Event"
        verbose_name_plural="Events"
        ordering=["id"]
    timestamp=models.DateTimeField("Timestamp")
    managed_object=models.ForeignKey(ManagedObject,verbose_name="Managed Object")
    event_priority=models.ForeignKey(EventPriority,verbose_name="Priority")
    event_category=models.ForeignKey(EventCategory,verbose_name="Event Category")
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    status=models.CharField("Status",max_length=1,choices=EVENT_STATUS_CHOICES,default="U")
    close_timestamp=models.DateTimeField("Close Timestamp",blank=True,null=True)
    active_till=models.DateTimeField("Active Till",blank=True,null=True)          # Time-based event closing
    root=models.ForeignKey("Event",verbose_name="Root cause",blank=True,null=True)# Set up by correlator, Null for root cause
    subject=models.CharField("Subject",max_length=256,null=True,blank=True)       # Not null when classified
    body=models.TextField("Body",null=True,blank=True)
    
    def __unicode__(self):
        return u"Event #%s: %s"%(str(self.id),str(self.subject))
    
    def _repeats(self):
        return self.eventrepeat_set.count()
    repeats=property(_repeats)
    
    def _data(self):
        r={}
        for d in self.eventdata_set.all():
            r[d.key]=d.value
        return r
    data=property(_data)
    
    def match_data(self,vars):
        data=self.data
        for k,v in vars.items():
            if k not in data or data[k]!=v:
                return False
        return True
    ##
    ## Reset event status to "Unclassified"
    ##
    def reclassify_event(self,message="Reclassification requested"):
        self.change_status("U",message)
    ##
    ## Close event
    ##
    def close_event(self,message="Event Closed"):
        self.change_status("C",message)
    ##
    ##
    ##
    def open_event(self,message="Event Opened"):
        self.change_status("A",message)
    ##
    ## Change event status
    ##
    def change_status(self,status,msg=None):
        if self.status==status:
            return
        if msg is None:
            msg="Status changed from %s to %s"%(self.status,status)
        from_status=self.status
        self.status=status
        self.save()
        self.log(msg,from_status,status)
    ##
    ## Log event processing message
    ##
    def log(self,msg,from_status=None,to_status=None):
        if from_status is None:
            from_status=self.status
        if to_status is None:
            to_status=self.status
        l=EventLog(event=self,timestamp=datetime.datetime.now(),from_status=from_status,to_status=to_status,message=msg)
        l.save()
##
## Event body
##
class EventData(models.Model):
    class Meta:
        verbose_name="Event Data"
        verbose_name_plural="Event Data"
        unique_together=[("event","key","type")]
    event=models.ForeignKey(Event,verbose_name="Event")
    key=models.CharField("Key",max_length=256)
    value=models.TextField("Value",blank=True,null=True)
    type=models.CharField("Type",max_length=1,choices=[(">","Received"),("V","Variable"),("R","Resolved")],default=">")
    ##
    ## Resolve MIBs in key/value part and fill out hint
    ##
    def _description(self):
        d=MIB.get_description(self.value)
        if d:
            return d
        return MIB.get_description(self.key)
    description=property(_description)
##
## Repeated events are deleated from Event table and only short record in EventRepeat remains
##
class EventRepeat(models.Model):
    class Meta:
        verbose_name="Event Repeat"
        verbose_name_plural="Event Repeats"
    event=models.ForeignKey(Event,verbose_name="Event")
    timestamp=models.DateTimeField("Timestamp")
##
## Event Processing Log
##
class EventLog(models.Model):
    class Meta:
        verbose_name="Event Log"
        verbose_name="Event Logs"
        ordering=["event","timestamp"]
    event=models.ForeignKey(Event,verbose_name="Event")
    timestamp=models.DateTimeField("Timestamp")
    from_status=models.CharField("From Status",max_length=1,choices=EVENT_STATUS_CHOICES)
    to_status=models.CharField("To Status",max_length=1,choices=EVENT_STATUS_CHOICES)
    message=models.TextField("Message")
##
##
##
class EventArchivationRule(models.Model):
    class Meta:
        verbose_name="Event Archivation Rule"
        verbose_name_plural="Event Archivation Rules"
        unique_together=[("event_class","action")]
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    ttl=models.IntegerField("Time To Live")
    ttl_measure=models.CharField("Measure",choices=[("s","Seconds"),("m","Minutes"),("h","Hours"),("d","Days")],default="h",max_length=1)
    action=models.CharField("Action",choices=[("C","Close"),("D","Drop")],default="D",max_length=1)
    def __unicode__(self):
        return u"%s: %s"%(self.event_class.name,self.action)
    ## Calculate ttl in seconds
    def _ttl_seconds(self):
        return self.ttl*{"s":1,"m":60,"h":3600,"d":86400}[self.ttl_measure]
    ttl_seconds=property(_ttl_seconds)
##
## Application Menu
##
class AppMenu(Menu):
    app="fm"
    title="Fault Management"
    items=[
        ("Events", "/fm/", "fm.change_event"),
        ("Active Problems", "/fm/active_problems_summary/", "fm.change_event"),
        ("Setup", [
            ("MIBs",                "/admin/fm/mib/",                     "fm.change_mib"),
            ("MIB Data",            "/admin/fm/mibdata/",                 "fm.change_mibdata"),
            ("Event Classes",       "/admin/fm/eventclass/",              "fm.change_eventclass"),
            ("Event Categories",    "/admin/fm/eventcategory/",           "fm.change_eventcategory"),
            ("Event Priorities",    "/admin/fm/eventpriority/",           "fm.change_eventpriority"),
            ("Classification Rules","/admin/fm/eventclassificationrule/", "fm.change_eventclassificationrule"),
            ("Post-Processing Rules", "/admin/fm/eventpostprocessingrule/", "fm.change_eventpostprocessingrule"),
            ("Correlation Rules",   "/admin/fm/eventcorrelationrule/",    "fm.change_eventcorrelationrule"),
            ("Archivation Rules",   "/admin/fm/eventarchivationrule/",    "fm.change_eventarchivationrule"),
        ])
    ]
