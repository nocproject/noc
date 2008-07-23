from django.db import models
from noc.lib.validators import check_asn

class LIR(models.Model):
    class Admin: pass
    class Meta:
        verbose_name="LIR"
        verbose_name_plural="LIRs"
    name=models.CharField("LIR name",unique=True,maxlength=64)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)

class AS(models.Model):
    class Admin:
        list_display=["asn","description","lir"]
        list_filter=["lir"]
        search_fields=["asn","description"]
    class Meta:
        verbose_name="AS"
        verbose_name_plural="ASes"
    lir=models.ForeignKey(LIR,verbose_name="LIR")
    asn=models.IntegerField("ASN",unique=True,validator_list=[check_asn])
    description=models.CharField("Description",maxlength=64)
    def __str__(self):
        return "AS%d (%s)"%(self.asn,self.description)
    def __unicode__(self):
        return u"AS%d (%s)"%(self.asn,self.description)
