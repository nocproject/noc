from django.db import models
from noc.sa.models import ManagedObject
import imp,subprocess,tempfile,os,datetime

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
            
    @classmethod
    def get_oid(cls,name):
        try:
            o=MIBData.objects.get(name=name)
            return o.oid
        except MIBData.DoesNotExist:
            return None
            
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
                    name+="."+".".join(rest)
                return name
            except MIBData.DoesNotExist:
                rest.append(l_oid.pop())
        return oid

class MIBData(models.Model):
    class Meta:
        verbose_name="MIB Data"
        verbose_name_plural="MIB Data"
        ordering=["oid"]
    mib = models.ForeignKey(MIB,verbose_name="MIB")
    oid = models.CharField("OID",max_length=128,unique=True)
    name= models.CharField("Name",max_length=128,unique=True)
    description= models.TextField("Description",blank=True,null=True)

class EventPriority(models.Model):
    class Meta:
        verbose_name="Event Priority"
        verbose_name_plural="Event Priorities"
        ordering=["priority"]
    name=models.CharField("Name",max_length=32,unique=True)
    priority=models.IntegerField("Priority")
    description=models.TextField("Description",blank=True,null=True)
    def __unicode__(self):
        return self.name

class EventClass(models.Model):
    class Meta:
        verbose_name="Event Class"
        verbose_name_plural="Event Classes"
        ordering=["name"]
    name=models.CharField("Name",max_length=32,unique=True)
    description=models.TextField("Description",blank=True,null=True)
    
    def __unicode__(self):
        return self.name

class Event(models.Model):
    class Meta:
        verbose_name="Event"
        verbose_name_plural="Events"
        ordering=[("id")]
    timestamp=models.DateTimeField("Timestamp")
    managed_object=models.ForeignKey(ManagedObject,verbose_name="Managed Object")
    event_priority=models.ForeignKey(EventPriority,verbose_name="Priority")
    event_class=models.ForeignKey(EventClass,verbose_name="Event Class")
    parent=models.ForeignKey("Event",verbose_name="Parent",blank=True,null=True) # Set up by correlator
    subject=models.CharField("Subject",max_length=256,null=True,blank=True)      # Not null when classified
    body=models.TextField("Body",null=True,blank=True)
    
    def __unicode__(self):
        return u"Event #%d: %s"%(self.id,str(self.subject))

class EventData(models.Model):
    class Meta:
        verbose_name="Event Data"
        verbose_name_plural="Event Data"
        unique_together=[("event","key")]
    event=models.ForeignKey(Event,verbose_name="Event")
    key=models.CharField("Key",max_length=64)
    value=models.TextField("Value",blank=True,null=True)
    is_enriched=models.BooleanField("Is Enriched",blank=True,null=True,default=False) # pair added by classifier
    
    def __unicode__(self):
        return u"Event #%d: %s=%s"%(self.id,self.key,self.value)

