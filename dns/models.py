# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for DNS module
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
import os
import time
import subprocess
# Django modules
from django.db import models
# NOC Modules
from noc.settings import config
from noc.ip.models import Address, AddressRange
from noc.lib.validators import is_ipv4
from noc.lib.fileutils import is_differ,rewrite_when_differ,safe_rewrite
from noc.dns.generators import generator_registry
from noc.lib.rpsl import rpsl_format
from noc.lib.fields import AutoCompleteTagsField
from noc.lib.app.site import site
from noc.lib.ip import *
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
            return u"%s (%s)"%(self.name,self.location)
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
    
    @property
    def generator_class(self):
        return generator_registry[self.generator_name]
    

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
    
    @property
    def authoritative_servers(self):
        return list(self.masters.all())+list(self.slaves.all())
    

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
    tags=AutoCompleteTagsField("Tags",null=True,blank=True)
    
    # Managers
    objects=models.Manager()
    forward_zones=ForwardZoneManager()
    reverse_zones=ReverseZoneManager()
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return site.reverse("dns:dnszone:change",self.id)
    
    @property
    def type(self):
        nl=self.name.lower()
        if nl.endswith(".in-addr.arpa"):
            return "R4" # IPv4 reverse
        elif nl.endswith(".ip6.int"):
            return "R6" # IPv6 reverse
        else:
            return "F"  # Forward
    
    rx_rzone=re.compile(r"^(\d+)\.(\d+)\.(\d+)\.in-addr.arpa$")
    @property
    def reverse_prefix(self):
        if self.type=="R4":
            # Get IPv4 prefix covering reverse zone
            match=self.rx_rzone.match(self.name.lower())
            if match:
                return "%s.%s.%s.0/24"%(match.group(3),match.group(2),match.group(1))
        elif self.type=="R6":
            # Get IPv6 prefix covering reverse zone
            p=self.name.lower()[:-8].split(".")
            p.reverse()
            l=len(p)
            if l%4:
                p+=["0"]*(4-l%4)
            r=""
            for i,c in enumerate(p):
                if i and i%4==0:
                    r+=":"
                r+=c
            if l!=32:
                r+="::"
            return IPv6(r+"/%d"%(l*4)).normalized.prefix
            
    
    @property
    def next_serial(self):
        T=time.gmtime()
        p="%04d%02d%02d"%(T[0],T[1],T[2])
        sn=int(self.serial[-2:])
        if self.serial.startswith(p):
            return p+"%02d"%(sn+1)
        return p+"00"
    
    ##
    ## Returns a list of zone's RR.
    ## [(left,type,right)]
    ##
    @property
    def records(self):
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
        
        records=[]
        if self.type=="F":
            # Populate forward zone from IPAM
            records=[
                    (
                        a.fqdn.split(".")[0],
                        "IN  A" if a.afi=="4" else "IN  AAAA",
                        a.address
                    )
                    for a in Address.objects.raw("""
                        SELECT id,address,afi,fqdn
                        FROM   %s
                        WHERE  domainname(fqdn)=%%s
                        ORDER BY address
                        """%Address._meta.db_table,[self.name])]
            order_by=cmp_fwd
        elif self.type=="R4":
            # Populate IPv4 reverse zone from IPAM
            records=[
                (
                    a.address.split(".")[3],
                    "PTR",
                    a.fqdn+"."
                )
                for a in Address.objects.raw("""
                    SELECT id,address,afi,fqdn
                    FROM %s
                    WHERE
                            address << %%s
                        AND afi='4'
                """%Address._meta.db_table,[self.reverse_prefix])
                ]
            order_by=cmp_ptr
        elif self.type=="R6":
            # Populate IPv6 reverse zone from IPAM
            origin_length=(len(self.name)-8+1)//2
            records=[
                (   
                    IPv6(a.address).ptr(origin_length),
                    "PTR",
                    a.fqdn+"."
                )
                for a in Address.objects.raw("""
                    SELECT id,address,afi,fqdn
                    FROM %s
                    WHERE
                            address << %%s
                        AND afi='6'
                """%Address._meta.db_table,[self.reverse_prefix])]
            order_by=cmp_fwd
        else:
            raise Exception,"Invalid zone type"
        # Add records from DNSZoneRecord
        zonerecords=self.dnszonerecord_set.all()
        if self.type=="R4":
            # Classles reverse zone delegation
            # Range delegations
            for r in AddressRange.objects.raw("""
                SELECT * FROM
                ip_addressrange
                WHERE
                        from_address<<%s
                    AND to_address<<%s
                    AND action='D'""",[self.reverse_prefix,self.reverse_prefix]):
                nses=[ns.strip() for ns in r.reverse_nses.split(",")]
                for a in r.addresses:
                    n=a.address.split(".")[-1]
                    records+=[[n,"CNAME","%s.%s/32"%(n,n)]]
                    for ns in nses:
                        records+=[["%s/32"%n,"IN NS",ns]]
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
    
    def zonedata(self,ns):
        return ns.generator_class().get_zone(self)
    
    @property
    def distribution_list(self):
        return self.profile.masters.filter(provisioning__isnull=False)
    
    def distribution(self):
        return ", ".join(["<A HREF='/dns/dnszone/%d/ns/%d/'>%s</A>"%(self.id,n.id,n.name) for n in self.distribution_list])
    distribution.short_description="Distribution"
    distribution.allow_tags=True
    
    @property
    def children(self):
        l=len(self.name)
        return [z for z in DNSZone.objects.filter(name__iendswith="."+self.name) if "." not in z.name[:-l-1]]
    
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
    
    @property
    def ns_list(self):
        return sorted([self.get_ns_name(ns) for ns in self.profile.authoritative_servers])
    
    @property
    def rpsl(self):
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
    tags=AutoCompleteTagsField("Tags",null=True,blank=True)
    def __unicode__(self):
        return u"%s %s"%(self.zone.name," ".join([x for x in [self.left,self.type.type,self.right] if x is not None]))

    def get_absolute_url(self):
        return site.reverse("dns:dnszone:change",self.zone.id)
        
