# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
from noc.sa.models import ManagedObject
import imp,subprocess,tempfile,os,datetime

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
        # Convert MIB to python module and load
        h,p=tempfile.mkstemp()
        subprocess.check_call(["smidump","-k","-f","python","-o",p,path])
        m=imp.load_source("mib",p)
        os.close(h)
        os.unlink(p)
        mib_name=m.MIB["moduleName"]
        # Get MIB latest revision date
        try:
            last_updated=datetime.datetime.strptime(sorted([x["date"] for x in m.MIB[mib_name]["revisions"]])[-1],"%Y-%m-%d %H:%M")
        except:
            last_updated=datetime.datetime(year=1970,month=1,day=1)
        # Check mib already uploaded
        try:
            o=MIB.objects.get(name=mib_name)
        except MIB.DoesNotExist:
            o=None
        if o:
            # Skip same version
            if o.last_updated>=last_updated:
                return
            # Remove old version and data
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("DELETE FROM %s WHERE mib_id=%%s"%MIBData._meta.db_table,[o.id])
            o.delete()
        mib_description=m.MIB[mib_name].get("description",None)
        mib=MIB(name=mib_name,description=mib_description,uploaded=datetime.datetime.now(),last_updated=last_updated)
        mib.save()
        if "nodes" not in m.MIB:
            return
        for node,v in m.MIB["nodes"].items():
            d=MIBData(mib=mib,oid=v["oid"],name="%s::%s"%(mib_name,node),description=v.get("description",None))
            d.save()
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
    name=models.CharField("Name",max_length=64)
    category=models.ForeignKey(EventCategory,verbose_name="Event Category")
    default_priority=models.ForeignKey(EventPriority,verbose_name="Default Priority")
    #variables=models.CharField("Variables",max_length=128,blank=True,null=True)
    subject_template=models.CharField("Subject Template",max_length=128)
    body_template=models.TextField("Body Template")
    last_modified=models.DateTimeField("last_modified",auto_now=True)
    repeat_suppression=models.BooleanField("Repeat Suppression",default=False)
    repeat_suppression_interval=models.IntegerField("Repeat Suppression interval (secs)",default=3600)
    
    def __unicode__(self):
        return self.name
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
    drop_event=models.BooleanField("Drop Event",default=False)
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
##
## Event itself
##
class Event(models.Model):
    class Meta:
        verbose_name="Event"
        verbose_name_plural="Events"
        ordering=[("id")]
    timestamp=models.DateTimeField("Timestamp")
    managed_object=models.ForeignKey(ManagedObject,verbose_name="Managed Object")
    event_priority=models.ForeignKey(EventPriority,verbose_name="Priority")
    event_category=models.ForeignKey(EventCategory,verbose_name="Event Category")
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    parent=models.ForeignKey("Event",verbose_name="Parent",blank=True,null=True) # Set up by correlator
    subject=models.CharField("Subject",max_length=256,null=True,blank=True)      # Not null when classified
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
## Repeated events are deleated from Event table and only short record in EventRepeat remains
##
class EventRepeat(models.Model):
    class Meta:
        verbose_name="Event Repeat"
        verbose_name_plural="Event Repeats"
    event=models.ForeignKey(Event,verbose_name="Event")
    timestamp=models.DateTimeField("Timestamp")
