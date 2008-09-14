import re,os,time,md5
from django.db import models
from noc.setup.models import Settings
from noc.ip.models import IPv4Address
from noc.lib.validators import is_ipv4
from noc.lib.fileutils import is_differ,rewrite_when_differ,safe_rewrite
# DNS Zone Generators
from noc.dns.bindv9_zone_generator import BINDv9ZoneGenerator

ZONE_GENERATORS={
    "BINDv9": BINDv9ZoneGenerator,
}


##
## DNSServerType.
## Please, do not modify table contents directly, use migrations instead.
## Values are hardcoded in provisioning
##
class DNSServerType(models.Model):
    class Meta:
        verbose_name="DNS Server Type"
        verbose_name_plural="DNS Servers Type"
    name=models.CharField("Name",max_length=32,unique=True)
    def __unicode__(self):
        return self.name
##
## DNS Server
##
class DNSServer(models.Model):
    class Meta:
        verbose_name="DNS Server"
        verbose_name_plural="DNS Servers"
    name=models.CharField("Name",max_length=64,unique=True)
    type=models.ForeignKey(DNSServerType,verbose_name="Type")
    description=models.CharField("Description",max_length=128,blank=True,null=True)
    location=models.CharField("Location",max_length=128,blank=True,null=True)
    provisioning=models.CharField("Provisioning",max_length=128,blank=True,null=True,
        help_text="Script for zone provisioning")
    def __unicode__(self):
        if self.location:
            return "%s (%s)"%(self.name,self.location)
        else:
            return self.name
    def provision_zones(self):
        if self.provisioning:
            os.environ["RSYNC_RSH"]=Settings.get("shell.ssh")
            os.chdir(os.path.join(Settings.get("dns.zone_cache"),self.name))
            cmd=self.provisioning%{
                "rsync": Settings.get("shell.rsync"),
                "ns"   : self.name
            }
            os.system(cmd)
##
##
##
class DNSZoneProfile(models.Model):
    class Meta:
        verbose_name="DNS Zone Profile"
        verbose_name_plural="DNS Zone Profiles"
    name=models.CharField("Name",max_length=32,unique=True)
    ns_servers=models.ManyToManyField(DNSServer,verbose_name="NS Servers")
    zone_transfer_acl=models.CharField("named zone transfer ACL",max_length=64)
    zone_soa=models.CharField("SOA",max_length=64)
    zone_contact=models.CharField("Contact",max_length=64)
    zone_refresh=models.IntegerField("Refresh",default=3600)
    zone_retry=models.IntegerField("Retry",default=900)
    zone_expire=models.IntegerField("Expire",default=86400)
    zone_ttl=models.IntegerField("TTL",default=3600)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def _ztacl(self):
        return "allow-transfer { %s; };"%self.zone_transfer_acl.replace("}","")
    ztacl=property(_ztacl)
##
## Managers for DNSZone
##
class ForwardZoneManager(models.Manager):
    def get_query_set(self):
        return super(ReverseZoneManager,self).get_query_set().exclude(name__endswith=".in-addr.arpa")
        
class ReverseZoneManager(models.Manager):
    def get_query_set(self):
        return super(ReverseZoneManager,self).get_query_set().filter(name__endswith=".in-addr.arpa")
##
##
rx_rzone=re.compile(r"^(\d+)\.(\d+)\.(\d+)\.in-addr.arpa$")
class DNSZone(models.Model):
    class Meta:
        verbose_name="DNS Zone"
        verbose_name_plural="DNS Zones"
    name=models.CharField("Domain",max_length=64,unique=True)
    description=models.CharField("Description",null=True,blank=True,max_length=64)
    is_auto_generated=models.BooleanField("Auto generated?")
    serial=models.CharField("Serial",max_length=10,default="0000000000")
    profile=models.ForeignKey(DNSZoneProfile,verbose_name="Profile")
    
    # Managers
    objects=models.Manager()
    forward_zones=ForwardZoneManager()
    reverse_zones=ReverseZoneManager()
    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name
    def _type(self):
        if self.name.endswith(".in-addr.arpa"):
            return "R"
        else:
            return "F"
    type=property(_type)
    def _reverse_prefix(self):
        match=rx_rzone.match(self.name)
        if match:
            return "%s.%s.%s.0/24"%(match.group(3),match.group(2),match.group(1))
    reverse_prefix=property(_reverse_prefix)
    def _next_serial(self):
        T=time.gmtime()
        p="%04d%02d%02d"%(T[0],T[1],T[2])
        sn=int(self.serial[-2:])
        if self.serial.startswith(p):
            return p+"%02d"%(sn+1)
        return p+"00"
    next_serial=property(_next_serial)
    
    def _records(self):
        from django.db import connection
        c=connection.cursor()
        if self.type=="F":
            c.execute("SELECT hostname(fqdn),ip FROM %s WHERE domainname(fqdn)=%%s ORDER BY ip"%IPv4Address._meta.db_table, [self.name])
            records=[[r[0],"IN  A",r[1]] for r in c.fetchall()]
        elif self.type=="R":
            c.execute("SELECT ip,fqdn FROM %s WHERE ip::cidr << %%s ORDER BY ip"%IPv4Address._meta.db_table,[self.reverse_prefix])
            records=[[r[0].split(".")[3],"PTR",r[1]+"."] for r in c.fetchall()]
        else:
            raise Exception,"Invalid zone type"
        # Add records from DNSZoneRecord
        zonerecords=self.dnszonerecord_set.all()
        if self.type=="R":
            # Subnet delegation macro
            delegations={}
            for d in [r for r in zonerecords if "NS" in r.type.type and "/" in r.left]:
                r=d.right
                l=d.left
                if l in delegations:
                    delegations[l].append(r)
                else:
                    delegations[l]=[r]
            for d,nses in delegations.items():
                try:
                    net,mask=[int(x) for x in l.split("/")]
                    if net<0 or net>255 or mask<=24 or mask>32:
                        raise Exception,"Invalid record"
                except:
                    records+=[[";; Invalid record: %s"%d,"IN NS","error"]]
                    continue
                for ns in nses:
                    records+=[[d,"IN NS",ns]]
                m=mask-24
                bitmask=((1<<m)-1)<<(8-m)
                if net&bitmask != net:
                    records+=[[";; Invalid network: %s"%d,"CNAME",d]]
                    continue
                for i in range(net,net+(1<<(8-m))):
                    records+=[["%d"%i,"CNAME","%d.%s"%(i,d)]]
            # Other records
            records+=[[x.left,x.type.type,x.right] for x in zonerecords\
                if ("NS" in x.type.type and "/" not in x.left) or "NS" not in x.type.type]
        else:
            records+=[[x.left,x.type.type,x.right] for x in zonerecords]
        # Add NS records if nesessary
        l=len(self.name)
        for z in self.children:
            for ns in z.ns_list:
                records+=[[z.name[:-l-1],"IN NS",ns]]
        records.sort(lambda x,y:cmp(x[0],y[0]))
        return records
    records=property(_records)
    
    @classmethod
    def get_zone_generator(cls,ns):
        t=ns.type.name
        if t not in ZONE_GENERATORS:
            raise Exception,"Unsupported DNS Server Type '%s'"%t
        return ZONE_GENERATORS[t]()
        
    def zonedata(self,ns):
        return self.get_zone_generator(ns).get_zone(self)
    
    ##
    ## Rewrites zone files and return a list of affected nameservers
    ##
    @classmethod
    def rewrite_zones(cls):
        cache_path=Settings.get("dns.zone_cache")
        to_rewrite_inc=False
        nses={}
        for z in DNSZone.objects.filter(is_auto_generated=True):
            to_rewrite=False
            for ns in z.profile.ns_servers.all():
                nses[ns]=None
            for ns in z.profile.ns_servers.all():
                cp=os.path.join(cache_path,ns.name,z.name)
                if is_differ(cp,z.zonedata(ns)):
                    z.serial=z.next_serial
                    z.save()
                    for ns in z.profile.ns_servers.all():
                        rewrite_when_differ(cp,z.zonedata(ns))
                    to_rewrite_inc=True
                    break
        if to_rewrite_inc:
            for ns in nses:
                inc_path=os.path.join(cache_path,ns.name,"autozones.conf")
                g=cls.get_zone_generator(ns)
                safe_rewrite(inc_path,g.get_include(ns))
        return nses.keys()
    
    def _distribution_list(self):
        return self.profile.ns_servers.filter(provisioning__isnull=False)
    distribution_list=property(_distribution_list)
    
    def distribution(self):
        return ", ".join(["<A HREF='/dns/%s/zone/%s/'>%s</A>"%(self.name,n.id,n.name) for n in self.distribution_list])
    distribution.short_description="Distribution"
    distribution.allow_tags=True
            
    @classmethod
    def sync_zones(cls):
        nses=cls.rewrite_zones()
        for ns in nses:
            ns.provision_zones()

    def _children(self):
        l=len(self.name)
        return [z for z in DNSZone.objects.filter(name__iendswith="."+self.name) if "." not in z.name[:-l-1]]
    children=property(_children)
    
    def _ns_list(self):
        nses=[]
        for ns in self.profile.ns_servers.all():
            n=ns.name.strip()
            if not is_ipv4(n) and not n.endswith("."):
                n+="."
            nses.append(n)
        return nses
    ns_list=property(_ns_list)
##
##
##
class DNSZoneRecordType(models.Model):
    class Meta:
        verbose_name="DNS Zone Record Type"
        verbose_name_plural="DNS Zone Record Types"
    type=models.CharField("Type",max_length=16,unique=True)
    is_visible=models.BooleanField("Is Visible?",default=True)
    def __str__(self):
        return self.type
    def __unicode__(self):
        return unicode(self.type)
##
##
##
class DNSZoneRecord(models.Model):
    class Meta: pass
    zone=models.ForeignKey(DNSZone,verbose_name="Zone") # ,edit_inline=models.TABULAR,num_extra_on_change=5)
    left=models.CharField("Left",max_length=32,blank=True,null=True)
    type=models.ForeignKey(DNSZoneRecordType,verbose_name="Type")
    right=models.CharField("Right",max_length=64) #,core=True)
    def __str__(self):
        return "%s %s"%(self.zone.name," ".join([x for x in [self.left,self.type.type,self.right] if x is not None]))
    def __unicode__(self):
        return unicode(str(self))