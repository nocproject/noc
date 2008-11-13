from django.db import models
from noc.lib.validators import check_asn,check_as_set,is_ipv4,is_cidr
from noc.lib.tt import tt_url,admin_tt_url
from noc.lib.rpsl import rpsl_format
from noc.setup.models import Settings
from noc.sa.profiles import profile_registry
from noc.cm.models import Object
import random,sets

class LIR(models.Model):
    class Meta:
        verbose_name="LIR"
        verbose_name_plural="LIRs"
    name=models.CharField("LIR name",unique=True,max_length=64)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)

class AS(models.Model):
    class Meta:
        verbose_name="AS"
        verbose_name_plural="ASes"
    lir=models.ForeignKey(LIR,verbose_name="LIR")
    asn=models.IntegerField("ASN",unique=True) # ,validator_list=[check_asn]
    description=models.CharField("Description",max_length=64)
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
    lg_rcmd=models.CharField("LG RCMD Url",max_length=128,blank=True,null=True,
        help_text="&lt;schema&gt;://&lt;user&gt;:&lt;password&gt;@host/, where &lt;schema&gt; is one of telnet, ssh")
    provision_rcmd=models.CharField("Provisioning URL",max_length=128,blank=True,null=True,
        help_text="&lt;schema&gt;://&lt;user&gt;:&lt;password&gt;@host/, where &lt;schema&gt; is one of telnet, ssh")
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
    def lg_command(self,query_type,query):
        try:
            lgc=LGQueryCommand.objects.get(profile_name=self.profile_name,query_type=query_type)
        except LGQueryCommand.DoesNotExist:
            return None
        query=self.profile.convert_prefix(query)
        return lgc.command%{"query":query}
    def sync_cm_prefix_list(self):
        if self.provision_rcmd is None:
            return
        peers_pl=sets.Set([])
        peers_pl.update([p.import_filter_name for p in self.peer_set.filter(import_filter_name__isnull=False) if p.import_filter_name.strip()])
        peers_pl.update([p.export_filter_name for p in self.peer_set.filter(export_filter_name__isnull=False) if p.export_filter_name.strip()])
        h=self.hostname+"/"
        l_h=len(h)
        for p in Object.objects.filter(handler_class_name="prefix-list").filter(repo_path__startswith=h):
            pl=p.path[l_h:]
            if pl not in peers_pl:
                p.delete()
            else:
                del peers_pl[pl]
        for pl in peers_pl:
            o=Object(handler_class_name="prefix-list",stream_url=self.provision_rcmd,profile_name=self.profile_name,repo_path=h+pl)
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
        ifaddrs={}
        peers={}
        for p in self.peer_set.all():
            ifaddrs[p.local_ip,p.masklen]=None
            peers[p.remote_ip,p.remote_asn]=None
        s=[]
        s+=["inet-rtr: %s"%self.hostname]
        s+=["local-as: AS%d"%self.local_as.asn]
        for ip,masklen in sorted(ifaddrs.keys(),lambda x,y:cmp(x[0],y[0])):
            s+=["ifaddr: %s masklen %d"%(ip,masklen)]
        for remote_ip,remote_as in sorted(peers.keys(),lambda x,y:cmp(x[0],y[0])):
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
        
class Peer(models.Model):
    class Meta:
        verbose_name="Peer"
        verbose_name_plural="Peers"
    peer_group=models.ForeignKey(PeerGroup,verbose_name="Peer Group")
    peering_point=models.ForeignKey(PeeringPoint,verbose_name="Peering Point")
    local_asn=models.ForeignKey(AS,verbose_name="Local AS")
    local_ip=models.IPAddressField("Local IP")
    masklen=models.PositiveIntegerField("Masklen",default=30)
    remote_asn=models.IntegerField("Remote AS")
    remote_ip=models.IPAddressField("Remote IP")
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
            s+=" action pref=%d;"%self.local_pref
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
## Looking glass query type
## Do not modify table manually, use migrations to populate data
##
class LGQueryType(models.Model):
    class Meta:
        verbose_name="LG Query Type"
        verbose_name_plural="LG Queries Types"
    name=models.CharField("Name",max_length=32,unique=True)
    def __unicode__(self):
        return self.name
##
## Looking glass commands
##
class LGQueryCommand(models.Model):
    class Meta:
        verbose_name="LG Query Command"
        verbose_name_plural="LG Quert Commands"
        unique_together=[("profile_name","query_type")]
    profile_name=models.CharField("Profile",max_length=128,choices=profile_registry.choices)
    query_type=models.ForeignKey(LGQueryType,verbose_name="LG Query Type")
    command=models.CharField("Command",max_length=128)
    def __unicode__(self):
        return "%s %s"%(self.profile_name,self.query_type.name)
    def _is_argument_required(self):
        return self.command and "%(query)s" in self.command
    is_argument_required=property(_is_argument_required)
##
## Looking glass query
## Used for exchange with LGD
##
class LGQuery(models.Model):
    class Meta:
        verbose_name="LG Query"
        verbose_name_plural="LG Queries"
        unique_together=[("remote_addr","query_id")]
    time=models.DateTimeField("Time",auto_now_add=True,auto_now=True)
    status=models.CharField("Status",max_length=1,
        choices=[("n","New"),("p","In Progress"),("f","Failure"),("c","Complete")],default="n")
    remote_addr=models.IPAddressField("REMOTE_ADDR")
    query_id=models.IntegerField("Query ID")
    peering_point=models.ForeignKey(PeeringPoint,verbose_name="Peering Point")
    query_type=models.ForeignKey(LGQueryType,verbose_name="Query Type")
    query=models.CharField("Query",max_length=128,null=True,blank=True)
    out=models.TextField("Out",default="")
    def __unicode__(self):
        return u"[%s] %s %s %s"%(self.status,self.peering_point,self.query_type,self.query)
    @classmethod
    def submit_query(cls,remote_addr,peering_point,query_type,query):
        q=LGQuery(status="n",peering_point=peering_point,query_type=query_type,query=query,
            remote_addr=remote_addr,query_id=random.randint(0,0x7FFFFFFF))
        q.save()
        return q