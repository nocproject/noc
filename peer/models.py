from django.db import models
from noc.lib.validators import check_asn,check_as_set
from noc.lib.tt import tt_url,admin_tt_url
from noc.lib.rpsl import rpsl_format

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
    rpsl_header=models.TextField("RPSL Header",null=True,blank=True)
    rpsl_footer=models.TextField("RPSL Footer",null=True,blank=True)
    def __str__(self):
        return "AS%d (%s)"%(self.asn,self.description)
    def __unicode__(self):
        return u"AS%d (%s)"%(self.asn,self.description)
    def _rpsl(self):
        sep="remark: %s"%("-"*72)
        s=[]
        if self.rpsl_header:
            s+=self.rpsl_header.split("\n")
        groups={}
        for peer in self.peer_set.all():
            groups[peer.peer_group.id]=None
        for pg in PeerGroup.objects.filter(id__in=groups.keys()):
            if pg.description:
                s+=[sep]
                s+=["remark: -- %s"%x for x in pg.description.split("\n")]
                s+=[sep]
            for peer in self.peer_set.filter(peer_group__exact=pg):
                s+=peer.rpsl.split("\n")
        if self.rpsl_footer:
            s+=[sep]
            s+=self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)

class ASSet(models.Model):
    class Admin:
        list_display=["name","description","members"]
        search_fields=["name","description","members"]
    class Meta:
        verbose_name="ASSet"
        verbose_name_plural="ASSets"
    name=models.CharField("Name",maxlength=32,unique=True,validator_list=[check_as_set])
    description=models.CharField("Description",maxlength=64)
    members=models.TextField("Members",null=True,blank=True)
    rpsl_header=models.TextField("RPSL Header",null=True,blank=True)
    rpsl_footer=models.TextField("RPSL Footer",null=True,blank=True)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unique(self.name)
    def _member_list(self):
        if self.members is None:
            return []
        m=self.members.replace(","," ").replace("\n"," ").replace("\r"," ").upper().split()
        m.sort()
        return m
    member_list=property(_member_list)
    def _rpsl(self):
        sep="remark: %s"%("-"*72)
        s=[]
        if self.rpsl_header:
            s+=self.rpsl_header.split("\n")
        for m in self.member_list:
            s+=["members: %s"%m]
        if self.rpsl_footer:
            s+=[sep]
            s+=self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)

class PeeringPointType(models.Model):
    class Admin:
        list_display=["name"]
    class Meta:
        verbose_name="Peering Point Type"
        verbose_name_plural="Peering Point Types"
    name=models.CharField("Name",maxlength=32,unique=True)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)

class PeeringPoint(models.Model):
    class Admin:
        list_display=["hostname","management_ip","type","communities"]
        list_filter=["type"]
        search_fields=["hostname","management_ip"]
    class Meta:
        verbose_name="Peering Point"
        verbose_name_plural="Peering Points"
    hostname=models.CharField("FQDN",maxlength=64,unique=True)
    management_ip=models.IPAddressField("IP",unique=True)
    type=models.ForeignKey(PeeringPointType,verbose_name="Type")
    communities=models.CharField("Import Communities",maxlength=128,blank=True,null=True)
    def __str__(self):
        return self.hostname
    def __unicode__(self):
        return unicode(self.hostname)

class PeerGroup(models.Model):
    class Admin:
        list_display=["name","description","communities"]
    class Meta:
        verbose_name="Peer Group"
        verbose_name_plural="Peer Groups"
    name=models.CharField("Name",maxlength=32,unique=True)
    description=models.CharField("Description",maxlength=64)
    communities=models.CharField("Import Communities",maxlength=128,blank=True,null=True)
    max_prefixes=models.IntegerField("Max. Prefixes",default=100)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)
        
class Peer(models.Model):
    class Admin:
        list_display=["peering_point","local_asn","remote_asn","import_filter","export_filter","local_ip","remote_ip","admin_tt_url","description","communities"]
        search_fields=["remote_asn","description"]
        list_filter=["peering_point"]
    class Meta:
        verbose_name="Peer"
        verbose_name_plural="Peers"
    peer_group=models.ForeignKey(PeerGroup,verbose_name="Peer Group")
    peering_point=models.ForeignKey(PeeringPoint,verbose_name="Peering Point")
    local_asn=models.ForeignKey(AS,verbose_name="Local AS")
    local_ip=models.IPAddressField("Local IP")
    remote_asn=models.IntegerField("Remote AS")
    remote_ip=models.IPAddressField("Remote IP")
    import_filter=models.CharField("Import filter",maxlength=64)
    local_pref=models.IntegerField("Local Pref",null=True,blank=True)
    export_filter=models.CharField("Export filter",maxlength=64)
    description=models.CharField("Description",maxlength=64,null=True,blank=True)
    tt=models.IntegerField("TT",blank=True,null=True)
    communities=models.CharField("Import Communities",maxlength=128,blank=True,null=True)   # In addition to PeerGroup.communities
                                                                                            # and PeeringPoint.communities
    max_prefixes=models.IntegerField("Max. Prefixes",default=100)
    def __str__(self):
        return "%s (%s@%s)"%(self.remote_asn,self.remote_ip,self.peering_point.hostname)
    def __unicode__(self):
        return unicode(str(self))
    def _tt_url(self):
        return tt_url(self)
    tt_url=property(_tt_url)
    def admin_tt_url(self):
        return admin_tt_url(self)
    admin_tt_url.short_description="TT"
    admin_tt_url.allow_tags=True
    def _all_communities(self):
        r={}
        for cl in [self.peering_point.communities,self.peer_group.communities,self.communities]:
            if cl is None:
                continue
            for c in cl.replace(","," ").split():
                r[c]=None
        c=r.keys()
        c.sort()
        return " ".join(c)
    all_communities=property(_all_communities)
    def _rpsl(self):
        s="import: from AS%d"%self.remote_asn
        if self.local_pref:
            s+=" action pref=%d;"%self.local_pref
        s+=" accept %s\n"%self.import_filter
        s+="export: to AS%s announce %s"%(self.remote_asn,self.export_filter)
        return s
    rpsl=property(_rpsl)