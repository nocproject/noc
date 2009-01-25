from django.db import models
import imp,subprocess,tempfile,os,datetime

class MIB(models.Model):
    class Meta:
        verbose_name="MIB"
        verbose_name_plural="MIBs"
        ordering=[("name")]
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",blank=True,null=True)
    uploaded=models.DateTimeField("Uploaded",auto_now_add=True)
    
    def __unicode__(self):
        return self.name
    
    @classmethod
    def load(self,path):
        h,p=tempfile.mkstemp()
        subprocess.check_call(["smidump","-k","-f","python","-o",p,path])
        m=imp.load_source("mib",p)
        os.close(h)
        os.unlink(p)
        mib_name=m.MIB["moduleName"]
        mib_description=m.MIB[mib_name].get("description",None)
        mib=MIB(name=mib_name,description=mib_description,uploaded=datetime.datetime.now())
        mib.save()
        if "nodes" not in m.MIB:
            return
        for node,v in m.MIB["nodes"].items():
            d=MIBData(mib=mib,oid=v["oid"],name="%s::%s"%(mib_name,node),description=v.get("description",None))
            d.save()
        

class MIBData(models.Model):
    class Meta:
        verbose_name="MIB Data"
        verbose_name_plural="MIB Data"
        ordering=[("oid")]
    mib = models.ForeignKey(MIB,verbose_name="MIB")
    oid = models.CharField("OID",max_length=128,unique=True)
    name= models.CharField("Name",max_length=128,unique=True)
    description= models.TextField("Description",blank=True,null=True)
    
