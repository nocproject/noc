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
from noc.lib.fields import INETField,InetArrayField
from noc.sa.profiles import profile_registry
from noc.main.models import NotificationGroup
from noc.cm.models import PrefixList
from noc.sa.models import AdministrativeDomain
from noc.main.menu import Menu
from noc.main.middleware import get_user
from noc.lib.fileutils import urlopen
from noc.lib.crypto import md5crypt
import random,time,logging,urllib,urllib2

##
## Exception classes
##
class RIRDBUpdateError(Exception): pass
##
try:
    import ssl
    # Use SSL-enabled version when possible
    RIPE_SYNCUPDATES_URL="https://syncupdates.db.ripe.net"
except ImportError:
    RIPE_SYNCUPDATES_URL="http://syncupdates.db.ripe.net"
##
##
##
class RIR(models.Model):
    class Meta:
        verbose_name="RIR"
        verbose_name_plural="RIRs"
        ordering=["name"]
    name=models.CharField("name",max_length=64,unique=True)
    whois=models.CharField("whois",max_length=64,blank=True,null=True)
    def __unicode__(self):
        return self.name
    # Update RIR's database API and returns report
    def update_rir_db(self,data,maintainer=None):
        rir="RIPE" if self.name=="RIPE NCC" else self.name
        return getattr(self,"update_rir_db_%s"%rir)(data,maintainer)
    # RIPE NCC Update API
    def update_rir_db_RIPE(self,data,maintainer):
        data=[x for x in data.split("\n") if x] # Strip empty lines
        if maintainer.password:
            data+=["password: %s"%maintainer.password]
        admin=maintainer.admins.all()[0]
        T=time.gmtime()
        data+=["changed: %s %04d%02d%02d"%(admin.email,T[0],T[1],T[2])]
        data+=["source: RIPE"]
        data="\n".join(data)
        try:
            f=urllib2.urlopen(url=RIPE_SYNCUPDATES_URL,data=urllib.urlencode({"DATA":data}))
            data=f.read()
        except urllib2.URLError,why:
            data="Update failed: %s"%why
        return data

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

class Maintainer(models.Model):
    class Meta:
        verbose_name="Maintainer"
        verbose_name_plural="Maintainers"
    maintainer=models.CharField("mntner",max_length=64,unique=True)
    description=models.CharField("description",max_length=64)
    password=models.CharField("Password",max_length=64,null=True,blank=True)
    rir=models.ForeignKey(RIR,verbose_name="RIR")
    admins=models.ManyToManyField(Person,verbose_name="admin-c")
    extra=models.TextField("extra",blank=True,null=True)
    def __unicode__(self):
        return self.maintainer
    def _rpsl(self):
        s=[]
        s+=["mntner: %s"%self.maintainer]
        s+=["descr: %s"%self.description]
        if self.password:
            s+=["auth: MD5-PW %s"%md5crypt(self.password)]
        s+=["admins: %s"%x.nic_hdl for x in self.admins.all()]
        s+=["mnt-by: %s"%self.maintainer]
        if self.extra:
            s+=[self.extra]
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)

class Organisation(models.Model):
    class Meta:
        verbose_name="Organisation"
        verbose_name_plural="Organisations"
    organisation=models.CharField("Organisation",max_length=128,unique=True) # NIC Handle
    org_name=models.CharField("Org. Name",max_length=128) # org-name:
    org_type=models.CharField("Org. Type",max_length=64,choices=[("LIR","LIR")]) # org-type:
    address=models.TextField("Address") # address: will be prepended automatically for each line
    mnt_ref=models.ForeignKey(Maintainer,verbose_name="Mnt. Ref") # mnt-ref
    def __unicode__(self):
        return u"%s (%s)"%(self.organisation,self.org_name)

class AS(models.Model):
    class Meta:
        verbose_name="AS"
        verbose_name_plural="ASes"
    asn=models.IntegerField("ASN",unique=True) # ,validator_list=[check_asn]
    as_name=models.CharField("AS Name",max_length=64,null=True,blank=True) # as-name RPSL Field
    description=models.CharField("Description",max_length=64) # RPSL descr field
    organisation=models.ForeignKey(Organisation,verbose_name="Organisation")
    administrative_contacts=models.ManyToManyField(Person,verbose_name="admin-c",related_name="as_administrative_contacts")
    tech_contacts=models.ManyToManyField(Person,verbose_name="tech-c",related_name="as_tech_contacts")
    maintainers=models.ManyToManyField(Maintainer,verbose_name="Maintainers",related_name="as_maintainers")
    routes_maintainers=models.ManyToManyField(Maintainer,verbose_name="Routes Maintainers",related_name="as_route_maintainers")
    header_remarks=models.TextField("Header Remarks",null=True,blank=True) # remarks: will be prepended automatically
    footer_remarks=models.TextField("Footer Remarks",null=True,blank=True) # remarks: will be prepended automatically
    rir=models.ForeignKey(RIR,verbose_name="RIR") # source:
    def __str__(self):
        return "AS%d (%s)"%(self.asn,self.description)
    def __unicode__(self):
        return u"AS%d (%s)"%(self.asn,self.description)
    @classmethod
    def default_as(cls):
        return AS.objects.get(asn=0)
    def _rpsl(self):
        sep="remarks: %s"%("-"*72)
        s=[]
        s+=["aut-num: AS%s"%self.asn]
        if self.as_name:
            s+=["as-name: %s"%self.as_name]
        if self.description:
            s+=["descr: %s"%x for x in self.description.split("\n")]
        s+=["org: %s"%self.organisation.organisation]
        # Add header remarks
        if self.header_remarks:
            s+=["remarks: %s"%x for x in self.header_remarks.split("\n")]
        # Find AS peers
        pg={} # Peer Group -> AS -> peering_point -> [(import, export, localpref, import_med, export_med, remark)]
        for peer in self.peer_set.filter(status="A"):
            if peer.peer_group not in pg:
                pg[peer.peer_group]={}
            if peer.remote_asn not in pg[peer.peer_group]:
                pg[peer.peer_group][peer.remote_asn]={}
            if peer.peering_point not in pg[peer.peer_group][peer.remote_asn]:
                pg[peer.peer_group][peer.remote_asn][peer.peering_point]=[]
            to_skip=False
            e_import_med=peer.effective_import_med
            e_export_med=peer.effective_export_med
            for p_import,p_export,localpref,import_med,export_med,remark in pg[peer.peer_group][peer.remote_asn][peer.peering_point]:
                if peer.import_filter==p_import and peer.export_filter==p_export and e_import_med==import_med and e_export_med==export_med:
                    to_skip=True
                    break
            if not to_skip:
                pg[peer.peer_group][peer.remote_asn][peer.peering_point]+=[(peer.import_filter,peer.export_filter,peer.effective_local_pref,e_import_med,e_export_med,peer.rpsl_remark)]
        # Build RPSL
        inverse_pref=config.getboolean("peer","rpsl_inverse_pref_style")
        for peer_group in pg:
            s+=[sep]
            s+=["remarks: -- %s"%x for x in peer_group.description.split("\n")]
            s+=[sep]
            for asn in sorted(pg[peer_group]):
                add_at=len(pg[peer_group][asn])!=1
                for pp in pg[peer_group][asn]:
                    for import_filter,export_filter,localpref,import_med,export_med,remark in pg[peer_group][asn][pp]:
                        # Prepend import and export with remark when given
                        if remark:
                            s+=["remarks: # %s"%remark]
                        # Build import statement
                        i_s="import: from AS%d"%asn
                        if add_at:
                            i_s+=" at %s"%pp.hostname
                        actions=[]
                        if localpref:
                            pref=(65535-localpref) if inverse_pref else localpref
                            actions+=["pref=%d;"%pref]
                        if import_med:
                            actions+=["med=%d;"%import_med]
                        if actions:
                            i_s+=" action "+" ".join(actions)
                        i_s+=" accept %s"%import_filter
                        s+=[i_s]
                        # Build export statement
                        e_s="export: to AS%d"%asn
                        if add_at:
                            e_s+=" at %s"%pp.hostname
                        if export_med:
                            e_s+=" action med=%d;"%export_med
                        e_s+=" announce %s"%export_filter
                        s+=[e_s]
        # Add contacts
        for c in self.administrative_contacts.order_by("nic_hdl"):
            s+=["admin-c: %s"%c.nic_hdl]
        for c in self.tech_contacts.order_by("nic_hdl"):
            s+=["tech-c: %s"%c.nic_hdl]
        # Add maintainers
        for m in self.maintainers.all():
            s+=["mnt-by: %s"%m.maintainer]
        for m in self.routes_maintainers.all():
            s+=["mnt-routes: %s"%m.maintainer]
        # Add footer remarks
        if self.footer_remarks:
            s+=["remarks: %s"%x for x in self.footer_remarks.split("\n")]
        return rpsl_format("\n".join(s))
    rpsl=property(_rpsl)
    
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
    ##
    def update_rir_db(self):
        return self.rir.update_rir_db(self.rpsl,self.maintainers.all()[0])

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
    enable_prefix_list_provisioning=models.BooleanField("Enable Prefix-List Provisioning",default=False)
    prefix_list_notification_group=models.ForeignKey(NotificationGroup,verbose_name="Prefix List Notification Group",null=True,blank=True)
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
            if p.local_backup_ip and p.remote_backup_ip:
                ifaddrs.add(p.local_backup_ip)
                peers[p.remote_backup_ip,p.remote_asn]=None
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

class PeerGroup(models.Model):
    class Meta:
        verbose_name="Peer Group"
        verbose_name_plural="Peer Groups"
    name=models.CharField("Name",max_length=32,unique=True)
    description=models.CharField("Description",max_length=64)
    communities=models.CharField("Import Communities",max_length=128,blank=True,null=True)
    max_prefixes=models.IntegerField("Max. Prefixes",default=100)
    local_pref=models.IntegerField("Local Pref",null=True,blank=True)
    import_med=models.IntegerField("Import MED",blank=True,null=True)
    export_med=models.IntegerField("Export MED",blank=True,null=True)
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
    local_backup_ip=INETField("Local Backup IP",null=True,blank=True)
    remote_asn=models.IntegerField("Remote AS")
    remote_ip=INETField("Remote IP")
    remote_backup_ip=INETField("Remote Backup IP",null=True,blank=True)
    status=models.CharField("Status",max_length=1,default="A",choices=[("P","Planned"),("A","Active"),("S","Shutdown")])
    import_filter=models.CharField("Import filter",max_length=64)
    local_pref=models.IntegerField("Local Pref",null=True,blank=True) # Override PeerGroup.local_pref
    import_med=models.IntegerField("Import MED",blank=True,null=True) # Override PeerGroup.import_med
    export_med=models.IntegerField("Export MED",blank=True,null=True) # Override PeerGroup.export_med
    export_filter=models.CharField("Export filter",max_length=64)
    description=models.CharField("Description",max_length=64,null=True,blank=True)
    rpsl_remark=models.CharField("RPSL Remark",max_length=64,null=True,blank=True)           # Peer remark to be shown in RPSL
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
    def admin_local_ip(self):
        r=[self.local_ip]
        if self.local_backup_ip:
            r+=[self.local_backup_ip]
        return "<BR/>".join(r)
    admin_local_ip.short_description="Local Address"
    admin_local_ip.allow_tags=True
    def admin_remote_ip(self):
        r=[self.remote_ip]
        if self.remote_backup_ip:
            r+=[self.remote_backup_ip]
        return "<BR/>".join(r)
    admin_remote_ip.short_description="Local Address"
    admin_remote_ip.allow_tags=True
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
    # <!> deprecated
    def _rpsl(self):
        s="import: from AS%d"%self.remote_asn
        s+=" at %s"%self.peering_point.hostname
        actions=[]
        local_pref=self.effective_local_pref
        if local_pref:
            # Select pref meaning
            if config.getboolean("peer","rpsl_inverse_pref_style"):
                pref=65535-local_pref # RPSL style
            else:
                pref=local_pref
            actions+=["pref=%d;"%pref]
        import_med=self.effective_import_med
        if import_med:
            actions+=["med=%d;"%import_med]
        if actions:
            s+=" action "+" ".join(actions)
        s+=" accept %s\n"%self.import_filter
        actions=[]
        export_med=self.effective_export_med
        if export_med:
            actions+=["med=%d;"%export_med]
        s+="export: to AS%s at %s"%(self.remote_asn,self.peering_point.hostname)
        if actions:
            s+=" action "+" ".join(actions)
        " announce %s"%self.export_filter
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
    ## Effective localpref: Peer specific or PeerGroup inherited
    ##
    def _effective_local_pref(self):
        if self.local_pref is not None:
            return self.local_pref
        return self.peer_group.local_pref
    effective_local_pref=property(_effective_local_pref)
    ##
    ## Effective import med: Peer specific or PeerGroup inherited
    ##
    def _effective_import_med(self):
        if self.import_med is not None:
            return self.import_med
        return self.peer_group.import_med
    effective_import_med=property(_effective_import_med)
    ##
    ## Effective export med: Peer specific or PeerGroup inherited
    ##
    def _effective_export_med(self):
        if self.export_med is not None:
            return self.export_med
        return self.peer_group.export_med
    effective_export_med=property(_effective_export_med)
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
    ## Returns boolean with update status
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
                try:
                    f=urlopen(url,auto_deflate=True)
                except:
                    logging.error("peer.update_whois_cache: Cannot fetch URL %s"%url)
                    return False
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
        return True
##
##
##
class PrefixListCache(models.Model):
    class Meta:
        verbose_name="Prefix List Cache"
        verbose_name_plural="Prefix List Cache"
    peering_point=models.ForeignKey(PeeringPoint,verbose_name="Peering Point")
    name=models.CharField("Name",max_length=64)
    data=InetArrayField("Data")
    strict=models.BooleanField("Strict")
    changed=models.DateTimeField("Changed",auto_now=True,auto_now_add=True)
    pushed=models.DateTimeField("Pushed",blank=True,null=True)
    def __unicode__(self):
        return u"%s/%s"%(self.peering_point.hostname,self.name)

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
        ("Prefix List Builder", "/peer/builder/prefix_list/", "peer.change_peer"),
        ("Setup",[
            ("Peer Groups",     "/admin/peer/peergroup/"    , "peer.change_peergroup"),
            ("Community Types", "/admin/peer/communitytype/", "peer.change_communitytype"),
            ("RIRs",            "/admin/peer/rir/",           "peer.change_rir"),
            ("Persons",         "/admin/peer/person/",        "peer.change_person"),
            ("Maintainers",     "/admin/peer/maintainer/"   ,"peer.change_maintainer"),
            ("Organisations",   "/admin/peer/organisation/"   ,"peer.change_organisation"),
        ])
    ]
