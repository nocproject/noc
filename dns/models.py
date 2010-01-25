# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re,os,time,subprocess
from django.db import models
from noc.settings import config
from noc.ip.models import IPv4Address
from noc.lib.validators import is_ipv4
from noc.lib.fileutils import is_differ,rewrite_when_differ,safe_rewrite
from noc.dns.generators import generator_registry
from noc.lib.rpsl import rpsl_format
from noc.lib.ip import generate_ips
from noc.main.menu import Menu

##
## register all generator classes
##
generator_registry.register_all()
##
## DNS Server
##
class DNSServer(models.Model):
    class Meta:
        verbose_name="DNS Server"
        verbose_name_plural="DNS Servers"
    name=models.CharField("Name",max_length=64,unique=True)
    generator_name=models.CharField("Generator",max_length=32,choices=generator_registry.choices)
    ip=models.IPAddressField("IP",null=True,blank=True)
    description=models.CharField("Description",max_length=128,blank=True,null=True)
    location=models.CharField("Location",max_length=128,blank=True,null=True)
    provisioning=models.CharField("Provisioning",max_length=128,blank=True,null=True,
        help_text="Script for zone provisioning")
    autozones_path=models.CharField("Autozones path",max_length=256,blank=True,null=True,
        default="autozones",help_text="Prefix for autozones in config files")
    def __unicode__(self):
        if self.location:
            return "%s (%s)"%(self.name,self.location)
        else:
            return self.name
    # Expands variables if any
    def expand_vars(self,str):
        return str%{
            "rsync"    : config.get("path","rsync"),
            "vcs_path" : config.get("cm","vcs_path"),
            "repo"     : config.get("cm","repo"),
            "ns"       : self.name,
            "ip"       : self.ip,
        }
    
    def provision_zones(self):
        if self.provisioning:
            env=os.environ.copy()
            env["RSYNC_RSH"]=config.get("path","ssh")
            cmd=self.expand_vars(self.provisioning)
            retcode=subprocess.call(cmd,shell=True,cwd=os.path.join(config.get("cm","repo"),"dns"),env=env)
            return retcode==0
            
    def _generator_class(self):
        return generator_registry[self.generator_name]
    generator_class=property(_generator_class)
##
##
##
class DNSZoneProfile(models.Model):
    class Meta:
        verbose_name="DNS Zone Profile"
        verbose_name_plural="DNS Zone Profiles"
    name=models.CharField("Name",max_length=32,unique=True)
    masters=models.ManyToManyField(DNSServer,verbose_name="Masters",related_name="masters",blank=True)
    slaves=models.ManyToManyField(DNSServer,verbose_name="Slaves",related_name="slaves",blank=True)
    zone_soa=models.CharField("SOA",max_length=64)
    zone_contact=models.CharField("Contact",max_length=64)
    zone_refresh=models.IntegerField("Refresh",default=3600)
    zone_retry=models.IntegerField("Retry",default=900)
    zone_expire=models.IntegerField("Expire",default=86400)
    zone_ttl=models.IntegerField("TTL",default=3600)
    description=models.TextField("Description",blank=True,null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def _authoritative_servers(self):
        return list(self.masters.all())+list(self.slaves.all())
    authoritative_servers=property(_authoritative_servers)

##
## Managers for DNSZone
##
class ForwardZoneManager(models.Manager):
    def get_query_set(self):
        return super(ForwardZoneManager,self).get_query_set().exclude(name__iendswith=".in-addr.arpa")
        
class ReverseZoneManager(models.Manager):
    def get_query_set(self):
        return super(ReverseZoneManager,self).get_query_set().filter(name__iendswith=".in-addr.arpa")
##
##
rx_rzone=re.compile(r"^(\d+)\.(\d+)\.(\d+)\.in-addr.arpa$")
class DNSZone(models.Model):
    class Meta:
        verbose_name="DNS Zone"
        verbose_name_plural="DNS Zones"
        ordering=["name"]
    name=models.CharField("Domain",max_length=64,unique=True)
    description=models.CharField("Description",null=True,blank=True,max_length=64)
    is_auto_generated=models.BooleanField("Auto generated?")
    serial=models.CharField("Serial",max_length=10,default="0000000000")
    profile=models.ForeignKey(DNSZoneProfile,verbose_name="Profile")
    paid_till=models.DateField("Paid Till",null=True,blank=True)
    
    # Managers
    objects=models.Manager()
    forward_zones=ForwardZoneManager()
    reverse_zones=ReverseZoneManager()
    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name
    def _type(self):
        if self.name.lower().endswith(".in-addr.arpa"):
            return "R"
        else:
            return "F"
    type=property(_type)
    def _reverse_prefix(self):
        match=rx_rzone.match(self.name.lower())
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
    ##
    ## Returns a list of zone's RR.
    ## [(left,type,right)]
    ##
    def _records(self):
        ## Compare two RRs.
        ## PTR records are compared as interger
        ## other - as strings
        def cmp_ptr(x,y):
            x1,x2,x3=x
            y1,y2,y3=y
            if "PTR" in x2 and "PTR" in y2:
                try:
                    return cmp(int(x1),int(y1))
                except ValueError:
                    pass
            return cmp(x1,y1)
        def cmp_fwd(x,y):
            x1,x2,x3=x
            y1,y2,y3=y
            r=cmp(x1,y1)
            if r==0:
                r=cmp(x2,y2)
            if r==0:
                r=cmp(x3,y3)
            return r
        from django.db import connection
        c=connection.cursor()
        if self.type=="F":
            c.execute("SELECT hostname(fqdn),ip FROM %s WHERE domainname(fqdn)=%%s ORDER BY ip"%IPv4Address._meta.db_table, [self.name])
            records=[[r[0],"IN  A",r[1]] for r in c.fetchall()]
            order_by=cmp_fwd
        elif self.type=="R":
            c.execute("SELECT ip,fqdn FROM %s WHERE ip::cidr << %%s ORDER BY ip"%IPv4Address._meta.db_table,[self.reverse_prefix])
            records=[[r[0].split(".")[3],"PTR",r[1]+"."] for r in c.fetchall()]
            order_by=cmp_ptr
        else:
            raise Exception,"Invalid zone type"
        # Add records from DNSZoneRecord
        zonerecords=self.dnszonerecord_set.all()
        if self.type=="R":
            # Classles reverse zone delegation
            # Range delegations
            c.execute("SELECT from_ip,to_ip,fqdn_action_parameter FROM ip_ipv4addressrange WHERE from_ip << %s::cidr AND to_ip<<%s::cidr AND fqdn_action='D'",
                [self.reverse_prefix,self.reverse_prefix])
            for from_ip,to_ip,fqdn_action_params in c.fetchall():
                nses=[ns.strip() for ns in fqdn_action_params.split(",")]
                for ip in generate_ips(from_ip,to_ip):
                    n=ip.split(".")[-1]
                    for ns in nses:
                        records+=[["%s/32"%n,"IN NS",ns]]
                        records+=[[n,"CNAME","%s.%s/32"%(n,n)]]
            # Subnet delegation macro
            delegations={}
            for d in [r for r in zonerecords if "NS" in r.type.type and "/" in r.left]:
                r=d.right
                l=d.left
                if l in delegations:
                    delegations[l].append(r)
                else:
                    delegations[l]=[r]
            # Perform classless reverse zone delegation
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
        suffix=".%s."%self.name
        l=len(self.name)
        for z in self.children:
            nested_nses=[]
            for ns in z.profile.authoritative_servers:
                ns_name=self.get_ns_name(ns)
                records+=[[z.name[:-l-1],"IN NS",ns_name]]
                if ns_name.endswith(suffix) and "." in ns_name[:-len(suffix)]: # Zone delegated to NS from the child zone
                    r=(ns_name[:-len(suffix)],ns.ip)
                    if r not in nested_nses:
                        nested_nses+=[r]
            if nested_nses: # Create A records for nested NSes
                for name,ip in nested_nses:
                    records+=[[name,"IN A",ip]]
        # Create missed A records for NSses from zone
        # Find in-zone NSes
        in_zone_nses={}
        for ns in self.profile.authoritative_servers:
            ns_name=self.get_ns_name(ns)
            if ns_name.endswith(suffix) and "." not in ns_name[:-len(suffix)]: # NS server from zone
                in_zone_nses[ns_name[:-len(suffix)]]=ns.ip
        # Find missed in-zone NSes
        for l,t,r in records:
            if l in in_zone_nses and t in ["A","IN A"]:
                del in_zone_nses[l]
        for name,ip in in_zone_nses.items():
            records+=[[name,"IN A",ip]]
        #
        return sorted(records,order_by)
    records=property(_records)
    
    def zonedata(self,ns):
        return ns.generator_class().get_zone(self)
    
    def _distribution_list(self):
        return self.profile.masters.filter(provisioning__isnull=False)
    distribution_list=property(_distribution_list)
    
    def distribution(self):
        return ", ".join(["<A HREF='/dns/%s/zone/%s/'>%s</A>"%(self.name,n.id,n.name) for n in self.distribution_list])
    distribution.short_description="Distribution"
    distribution.allow_tags=True

    def _children(self):
        l=len(self.name)
        return [z for z in DNSZone.objects.filter(name__iendswith="."+self.name) if "." not in z.name[:-l-1]]
    children=property(_children)
    ##
    ## Add missed "." to the end of NS name in case of FQDN
    ##
    @classmethod
    def get_ns_name(cls,ns):
        name=ns.name.strip()
        if not is_ipv4(name) and not name.endswith("."):
            return name+"."
        else:
            return name
        
    def _ns_list(self):
        return sorted([self.get_ns_name(ns) for ns in self.profile.authoritative_servers])
    ns_list=property(_ns_list)
    
    def _rpsl(self):
        if self.type!="R":
            return ""
        # Do not generate RPSL for private reverse zones
        if self.name.lower().endswith(".10.in-addr.arpa"):
            return ""
        n1,n2,n=self.name.lower().split(".",2)
        if n>="16.172.in-addr.arpa" and n<="31.172.in-addr.arpa":
            return ""
        n1,n=self.name.lower().split(".",1)
        if n=="168.192.in-addr.arpa":
            return ""
        s=["domain: %s"%self.name]+["nserver: %s"%ns for ns in self.ns_list]
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    
    def rpsl_link(self):
        return "<A HREF='/dns/%s/zone/rpsl/'>RPSL</A>"%self.name
    rpsl_link.short_description="RPSL"
    rpsl_link.allow_tags=True
##
##
##
class DNSZoneRecordType(models.Model):
    class Meta:
        verbose_name="DNS Zone Record Type"
        verbose_name_plural="DNS Zone Record Types"
        ordering=["type"]
    type=models.CharField("Type",max_length=16,unique=True)
    is_visible=models.BooleanField("Is Visible?",default=True)
    validation=models.CharField("Validation",max_length=256,blank=True,null=True,
        help_text="Regular expression to validate record. Following macros can be used: OCTET, IPv4, FQDN")
    def __str__(self):
        return self.type
    def __unicode__(self):
        return unicode(self.type)
    @classmethod
    def interpolate_re(self,rx):
        for m,s in [
            ("OCTET",r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"),
            ("IPv4", r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"),
            ("FQDN", r"([a-z0-9\-]+\.?)*"),]:
            rx=rx.replace(m,s)
        return "^%s$"%rx
    def is_valid(self,value):
        if self.validation:
            rx=DNSZoneRecordType.interpolate_re(self.validation)
            return re.match(rx,value) is not None
        else:
            return True
    def save(self):
        if self.validation:
            try:
                rx=DNSZoneRecordType.interpolate_re(self.validation)
            except:
                raise Exception("Invalid regular expression: %s"%rx)
            try:
                re.compile(rx)
            except:
                raise Exception("Invalid regular expression: %s"%rx)
        super(DNSZoneRecordType,self).save()
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
##
## Application Menu
##
class AppMenu(Menu):
    app="dns"
    title="DNS"
    items=[
        ("Zones", "/admin/dns/dnszone/", "dns.change_dnszone"),
        ("Setup",[
            ("DNS Servers",      "/admin/dns/dnsserver/",         "dns.change_dnsserver"),
            ("Zone Profiles",    "/admin/dns/dnszoneprofile/",    "dns.change_dnszoneprofile"),
            ("Zone Record Types","/admin/dns/dnszonerecordtype/", "dns.change_dnszonerecordtype"),
        ])
    ]
