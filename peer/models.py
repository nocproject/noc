# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models
from noc.settings import config
from noc.lib.validators import check_asn,check_as_set,is_ipv4,is_cidr
from noc.lib.tt import tt_url,admin_tt_url
from noc.lib.rpsl import rpsl_format
from noc.lib.fields import INETField
from noc.sa.profiles import profile_registry
from noc.cm.models import PrefixList
from noc.sa.models import AdministrativeDomain
from noc.main.menu import Menu
from noc.lib.fileutils import urlopen
import random

class RIR(models.Model):
    class Meta:
        verbose_name="RIR"
        verbose_name_plural="RIRs"
        ordering=["name"]
    name=models.CharField("name",max_length=64,unique=True)
    whois=models.CharField("whois",max_length=64,blank=True,null=True)
    def __unicode__(self):
        return self.name

class Person(models.Model):
    class Meta:
        verbose_name="Person"
        verbose_name_plural="Persons"
    nic_hdl=models.CharField("nic-hdl",max_length=64,unique=True)
    person=models.CharField("person",max_length=128)
    address=models.TextField("address")
    phone=models.TextField("phone")
    fax_no=models.TextField("fax-no",blank=True,null=True)
    email=models.TextField("email")
    rir=models.ForeignKey(RIR,verbose_name="RIR")
    extra=models.TextField("extra",blank=True,null=True)
    def __unicode__(self):
        return "%s (%s)"%(self.nic_hdl,self.person)
    def _rpsl(self):
        s=[]
        s+=["person: %s"%self.person]
        s+=["nic-hdl: %s"%self.nic_hdl]
        s+=["address: %s"%x for x in self.address.split("\n")]
        s+=["phone: %s"%x for x in self.phone.split("\n")]
        if self.fax_no:
            s+=["fax-no: %s"%x for x in self.fax_no.split("\n")]
        s+=["email: %s"%x for x in self.email.split("\n")]
        if self.extra:
            s+=[self.extra]
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    def rpsl_link(self):
        return "<A HREF='/peer/person/%d/rpsl/'>RPSL</A>"%self.id
    rpsl_link.short_description="RPSL"
    rpsl_link.allow_tags=True

class Maintainer(models.Model):
    class Meta:
        verbose_name="Maintainer"
        verbose_name_plural="Maintainers"
    maintainer=models.CharField("mntner",max_length=64,unique=True)
    description=models.CharField("description",max_length=64)
    auth=models.TextField("auth")
    rir=models.ForeignKey(RIR,verbose_name="RIR")
    admins=models.ManyToManyField(Person,verbose_name="admin-c")
    extra=models.TextField("extra",blank=True,null=True)
    def __unicode__(self):
        return self.maintainer
    def _rpsl(self):
        s=[]
        s+=["mntner: %s"%self.maintainer]
        s+=["descr: %s"%self.description]
        s+=["auth: %s"%x for x in self.auth.split("\n")]
        s+=["admins: %s"%x.nic_hdl for x in self.admins.all()]
        s+=["mnt-by: %s"%self.maintainer]
        if self.extra:
            s+=[self.extra]
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    def rpsl_link(self):
        return "<A HREF='/peer/maintainer/%d/rpsl/'>RPSL</A>"%self.id
    rpsl_link.short_description="RPSL"
    rpsl_link.allow_tags=True

class AS(models.Model):
    class Meta:
        verbose_name="AS"
        verbose_name_plural="ASes"
    maintainer=models.ForeignKey(Maintainer,verbose_name="Maintainer")
    asn=models.IntegerField("ASN",unique=True) # ,validator_list=[check_asn]
    description=models.CharField("Description",max_length=64)
    rpsl_header=models.TextField("RPSL Header",null=True,blank=True)
    rpsl_footer=models.TextField("RPSL Footer",null=True,blank=True)
    def __str__(self):
        return "AS%d (%s)"%(self.asn,self.description)
    def __unicode__(self):
        return u"AS%d (%s)"%(self.asn,self.description)
    @classmethod
    def default_as(cls):
        return AS.objects.get(asn=0)
    def _rpsl(self):
        sep="remark: %s"%("-"*72)
        s=[]
        if self.rpsl_header:
            s+=self.rpsl_header.split("\n")
        s+=["aut-num: AS%s"%self.asn]
        groups={}
        peers={}
        for peer in self.peer_set.all():
            groups[peer.peer_group.id]=None
        for pg in PeerGroup.objects.filter(id__in=groups.keys()):
            if pg.description:
                s+=[sep]
                s+=["remark: -- %s"%x for x in pg.description.split("\n")]
                s+=[sep]
            for peer in self.peer_set.filter(peer_group__exact=pg):
                rpsl=peer.rpsl
                if rpsl in peers:
                    continue
                peers[rpsl]=None
                s+=rpsl.split("\n")
        if self.rpsl_footer:
            s+=[sep]
            s+=self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    
    def rpsl_link(self):
        return "<A HREF='/peer/AS/%d/rpsl/'>RPSL</A>"%self.asn
    rpsl_link.short_description="RPSL"
    rpsl_link.allow_tags=True
    
    def _dot(self):
        s=["graph {"]
        all_peers=Peer.objects.filter(local_asn__exact=self)
        uplinks={}
        peers={}
        downlinks={}
        for p in all_peers:
            if p.import_filter=="ANY" and p.export_filter!="ANY":
                uplinks[p.remote_asn]=p
            elif p.export_filter=="ANY":
                downlinks[p.remote_asn]=p
            else:
                peers[p.remote_asn]=p
        asn="AS%d"%self.asn
        for subgraph,peers in [("uplinks",uplinks.values()),("peers",peers.values()),("downlinks",downlinks.values())]:
            s+=["subgraph %s {"%subgraph]
            for p in peers:
                attrs=["taillabel=\"%s\""%p.import_filter,"headlabel=\"%s\""%p.export_filter]
                if p.import_filter=="ANY":
                    attrs+=["arrowtail=open"]
                if p.export_filter=="ANY":
                    attrs+=["arrothead=open"]
                s+=["    %s -- AS%d [%s];"%(asn,p.remote_asn,",".join(attrs))]
            s+=["}"]
        s+=["}"]
        return "\n".join(s)
    dot=property(_dot)

class CommunityType(models.Model):
    class Meta:
        verbose_name="Community Type"
        verbose_name_plural="Community Types"
    name=models.CharField("Description",max_length=32,unique=True)
    def __unicode__(self):
        return self.name

class Community(models.Model):
    class Meta:
        verbose_name="Community"
        verbose_name_plural="Communities"
    community=models.CharField("Community",max_length=20,unique=True)
    type=models.ForeignKey(CommunityType,verbose_name="Type")
    description=models.CharField("Description",max_length=64)
    def __unicode__(self):
        return self.community

class ASSet(models.Model):
    class Meta:
        verbose_name="ASSet"
        verbose_name_plural="ASSets"
    name=models.CharField("Name",max_length=32,unique=True) # ,validator_list=[check_as_set]
    description=models.CharField("Description",max_length=64)
    members=models.TextField("Members",null=True,blank=True)
    rpsl_header=models.TextField("RPSL Header",null=True,blank=True)
    rpsl_footer=models.TextField("RPSL Footer",null=True,blank=True)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)
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
        s+=["as-set: %s"%self.name]
        for m in self.member_list:
            s+=["members: %s"%m]
        if self.rpsl_footer:
            s+=[sep]
            s+=self.rpsl_footer.split("\n")
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    def rpsl_link(self):
        return "<A HREF='/peer/AS-SET/%s/rpsl/'>RPSL</A>"%self.name
    rpsl_link.short_description="RPSL"
    rpsl_link.allow_tags=True

class PeeringPoint(models.Model):
    class Meta:
        verbose_name="Peering Point"
        verbose_name_plural="Peering Points"
    hostname=models.CharField("FQDN",max_length=64,unique=True)
    location=models.CharField("Location",max_length=64,blank=True,null=True)
    local_as=models.ForeignKey(AS,verbose_name="Local AS")
    router_id=models.IPAddressField("Router-ID",unique=True)
    profile_name=models.CharField("Profile",max_length=128,choices=profile_registry.choices)
    communities=models.CharField("Import Communities",max_length=128,blank=True,null=True)
    def __str__(self):
        if self.location:
            return "%s (%s)"%(self.hostname,self.location)
        else:
            return self.hostname
    def __unicode__(self):
        if self.location:
            return u"%s (%s)"%(self.hostname,self.location)
        else:
            return self.hostname
    def sync_cm_prefix_list(self):
        peers_pl=set([])
        peers_pl.update([p.import_filter_name for p in self.peer_set.filter(import_filter_name__isnull=False) if p.import_filter_name.strip()])
        peers_pl.update([p.export_filter_name for p in self.peer_set.filter(export_filter_name__isnull=False) if p.export_filter_name.strip()])
        h=self.hostname+"/"
        l_h=len(h)
        for p in PrefixList.objects.filter(repo_path__startswith=h):
            pl=p.path[l_h:]
            if pl not in peers_pl:
                p.delete()
            else:
                del peers_pl[pl]
        for pl in peers_pl:
            o=PrefixList(repo_path=h+pl)
            o.save()
    #
    # Returns a list of (prefix-list-name, rpsl-filter)
    #
    def _generated_prefix_lists(self):
        pls={}
        for pr in self.peer_set.all():
            if pr.import_filter_name:
                pls[pr.import_filter_name]=pr.import_filter
            if pr.export_filter_name:
                pls[pr.export_filter_name]=pr.export_filter
        return pls.items()
    generated_prefix_lists=property(_generated_prefix_lists)
    #
    def _profile(self):
        return profile_registry[self.profile_name]()
    profile=property(_profile)
    #
    def _rpsl(self):
        ifaddrs=set()
        peers={}
        for p in self.peer_set.all():
            ifaddrs.add(p.local_ip)
            peers[p.remote_ip,p.remote_asn]=None
        s=[]
        s+=["inet-rtr: %s"%self.hostname]
        s+=["local-as: AS%d"%self.local_as.asn]
        for ip in sorted(ifaddrs):
            if "/" in ip:
                ip,masklen=ip.split("/")
            else:
                masklen="30"
            s+=["ifaddr: %s masklen %s"%(ip,masklen)]
        for remote_ip,remote_as in sorted(peers.keys(),lambda x,y:cmp(x[0],y[0])):
            if "/" in remote_ip:
                remote_ip,masklen=remote_ip.split("/")
            s+=["peer: BGP4 %s asno(%s)"%(remote_ip,remote_as)]
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    def rpsl_link(self):
        return "<A HREF='/peer/INET-RTR/%s/rpsl/'>RPSL</A>"%self.hostname
    rpsl_link.short_description="RPSL"
    rpsl_link.allow_tags=True

class PeerGroup(models.Model):
    class Meta:
        verbose_name="Peer Group"
        verbose_name_plural="Peer Groups"
    name=models.CharField("Name",max_length=32,unique=True)
    description=models.CharField("Description",max_length=64)
    communities=models.CharField("Import Communities",max_length=128,blank=True,null=True)
    max_prefixes=models.IntegerField("Max. Prefixes",default=100)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)
##
## BGP Peer
##
class Peer(models.Model):
    class Meta:
        verbose_name="Peer"
        verbose_name_plural="Peers"
    peer_group=models.ForeignKey(PeerGroup,verbose_name="Peer Group")
    peering_point=models.ForeignKey(PeeringPoint,verbose_name="Peering Point")
    local_asn=models.ForeignKey(AS,verbose_name="Local AS")
    local_ip=INETField("Local IP")
    remote_asn=models.IntegerField("Remote AS")
    remote_ip=INETField("Remote IP")
    import_filter=models.CharField("Import filter",max_length=64)
    local_pref=models.IntegerField("Local Pref",null=True,blank=True)
    export_filter=models.CharField("Export filter",max_length=64)
    description=models.CharField("Description",max_length=64,null=True,blank=True)
    tt=models.IntegerField("TT",blank=True,null=True)
    communities=models.CharField("Import Communities",max_length=128,blank=True,null=True)   # In addition to PeerGroup.communities
                                                                                            # and PeeringPoint.communities
    max_prefixes=models.IntegerField("Max. Prefixes",default=100)
    import_filter_name=models.CharField("Import Filter Name",max_length=64,blank=True,null=True)
    export_filter_name=models.CharField("Export Filter Name",max_length=64,blank=True,null=True)
    def __str__(self):
        return "%s (%s@%s)"%(self.remote_asn,self.remote_ip,self.peering_point.hostname)
    def __unicode__(self):
        return unicode(str(self))
    def save(self):
        if self.import_filter_name is not None and not self.import_filter_name.strip():
            self.import_filter_name=None
        if self.export_filter_name is not None and not self.export_filter_name.strip():
            self.export_filter_name=None
        super(Peer,self).save()
        self.peering_point.sync_cm_prefix_list()
    def _tt_url(self):
        return tt_url(self)
    tt_url=property(_tt_url)
    def admin_tt_url(self):
        return admin_tt_url(self)
    admin_tt_url.short_description="TT"
    admin_tt_url.allow_tags=True
    def admin_import_filter(self):
        r=[]
        if self.import_filter:
            r.append(self.import_filter)
        if self.import_filter_name:
            r.append("(%s)"%self.import_filter_name)
        return "<BR/>".join(r)
    admin_import_filter.short_description="Import Filter"
    admin_import_filter.allow_tags=True
    def admin_export_filter(self):
        r=[]
        if self.export_filter:
            r.append(self.export_filter)
        if self.export_filter_name:
            r.append("(%s)"%self.export_filter_name)
        return "<BR/>".join(r)
    admin_export_filter.short_description="Export Filter"
    admin_export_filter.allow_tags=True
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
        s+=" at %s"%self.peering_point.hostname
        if self.local_pref:
            # Select pref meaning
            if config.getboolean("peer","rpsl_inverse_pref_style"):
                pref=65535-self.local_pref # RPSL style
            else:
                pref=self.local_pref                
            s+=" action pref=%d;"%pref
        s+=" accept %s\n"%self.import_filter
        s+="export: to AS%s at %s announce %s"%(self.remote_asn,self.peering_point.hostname,self.export_filter)
        return s
    rpsl=property(_rpsl)
    def _effective_max_prefixes(self):
        if self.max_prefixes:
            return self.max_prefixes
        if self.peer_group.max_prefixes:
            return self.peer_group.max_prefixes
        return 0
    effective_max_prefixes=property(_effective_max_prefixes)
##
## Whois Database
##
class WhoisDatabase(models.Model):
    class Meta:
        verbose_name="Whois Database"
        verbose_name_plural="Whois Databases"
    name=models.CharField("Name",unique=True,max_length=32)
    def __unicode__(self):
        return self.name
    #
    def parse(self,f,fields=None):
        return getattr(self,"parse_%s"%self.name)(f,fields)
    #
    @classmethod
    def parse_RIPE(self,f,fields=None):
        obj={}
        for l in f:
            l=l.strip()
            if l.startswith("#"):
                continue
            if l=="":
                # New object
                if obj:
                    yield obj
                    obj={}
                continue
            if "#" in l:
                l,r=l.split("#",1)
            if ":" in l:
                k,v=[x.strip() for x in l.split(":",1)]
                if fields and k not in fields:
                    continue
                if k in obj:
                    obj[k]+=[v]
                else:
                    obj[k]=[v]
        if obj:
            yield obj
##
##
##
class WhoisLookup(models.Model):
    class Meta:
        unique_together=[("whois_database","url","key","value")]
    whois_database=models.ForeignKey(WhoisDatabase,verbose_name="Whois Database")
    url=models.CharField("URL",max_length=256)
    direction=models.CharField("Direction",max_length=1,choices=[("F","Forward"),("R","Reverse")])
    key=models.CharField("Key",max_length=32)
    value=models.CharField("Value",max_length=32)
    def __unicode__(self):
        return u"(%s:%s:%s:%s)"%(self.whois_database.name,self.direction,self.key,self.value)
    # method is key:value
    #
    @classmethod
    def lookup(self,method,query):
        key,value=method.split(":")
        lookup_ids=[l.id for l in WhoisLookup.objects.filter(key=key,value=value)]
        r=list(WhoisCache.objects.filter(lookup__in=lookup_ids,key=query))
        if len(r)==0:
            return set()
        return set(r[0].value.split("|"))
##
##
##
class WhoisCache(models.Model):
    class Meta:
        verbose_name="Whois Cache"
        verbose_name_plural="Whois Cache"
        unique_together=[("lookup","key")]
    lookup=models.ForeignKey(WhoisLookup,verbose_name="Whois Lookup")
    key=models.CharField("Key",max_length=64)
    value=models.TextField("Value")
    ##
    ## Fetch data into cache
    ##
    @classmethod
    def update(cls):
        WhoisCache.objects.all().delete()
        lt={}
        for wdb in WhoisDatabase.objects.all():
            # Fetch
            urls={}
            for wl in wdb.whoislookup_set.all():
                if wl.url not in urls:
                    urls[wl.url]=[wl]
                else:
                    urls[wl.url]+=[wl]
            #
            for url in urls:
                fields=set()
                f_set=[]
                r_set=[]
                for wl in urls[url]:
                    fields.add(wl.key)
                    fields.add(wl.value)
                    if wl.direction=="F":
                        f_set+=[wl]
                    else:
                        r_set+=[wl]
                # Fetch
                f=urlopen(url,auto_deflate=True)
                data=list(wdb.parse(f,fields))
                f.close()
                # Process forward lookups
                for wl in f_set:
                    key=wl.key
                    value=wl.value
                    for d in data:
                        k=d[key][0]
                        try:
                            v=d[value]
                        except KeyError:
                            v=[]
                        v=",".join(v)
                        v="|".join([x.strip() for x in v.split(",")])
                        wc=WhoisCache(lookup=wl,key=k,value=v)
                        wc.save()
                # Process reverse lookups
                for wl in r_set:
                    key=wl.key
                    value=wl.value
                    result={}
                    for d in data:
                        try:
                            k=d[key]
                        except KeyError:
                            continue
                        try:
                            v=d[value][0]
                        except KeyError:
                            continue
                        k=",".join(k)
                        k="|".join([x.strip() for x in k.split(",")])
                        for k in k.split("|"):
                            try:
                                result[k].add(v)
                            except KeyError:
                                result[k]=set([v])
                    for key,value in result.items():
                        wc=WhoisCache(lookup=wl,key=key,value="|".join(value))
                        wc.save()

##
## Application Menu
##
class AppMenu(Menu):
    app="peer"
    title="Peering Management"
    items=[
        ("ASes",          "/admin/peer/as/"           ,"peer.change_as"),
        ("ASsets",        "/admin/peer/asset/"        ,"peer.change_asset"),
        ("Communities",   "/admin/peer/community/"    ,"peer.change_community"),
        ("Peering Points","/admin/peer/peeringpoint/" ,"peer.change_peeringpoint"),
        ("Peers",         "/admin/peer/peer/"         ,"peer.change_peer"),
        ("Setup",[
            ("Peer Groups",     "/admin/peer/peergroup/"    , "peer.change_peergroup"),
            ("Community Types", "/admin/peer/communitytype/", "peer.change_communitytype"),
            ("RIRs",            "/admin/peer/rir/",           "peer.change_rir"),
            ("Persons",         "/admin/peer/person/",        "peer.change_person"),
        ])
    ]
