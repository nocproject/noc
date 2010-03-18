# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
from django.db import models,connection
from django.db.models import Q
from django.contrib.auth.models import User
from noc.lib.validators import check_rd,check_cidr,is_cidr,is_ipv4
from noc.lib.tt import tt_url
from noc.peer.models import AS
from noc.vc.models import VC
from noc.lib.fields import CIDRField
from noc.lib.ip import int_to_address,bits_to_int,wildcard,broadcast,address_to_int,generate_ips,prefix_to_size
from noc.main.menu import Menu
from noc.main.search import SearchResult
from noc.main.middleware import get_user
##
##
##
class VRFGroup(models.Model):
    class Meta:
        verbose_name="VRF Group"
        verbose_name_plural="VRF Groups"
    name=models.CharField("VRF Group",unique=True,max_length=64)
    unique_addresses=models.BooleanField("Unique addresses in group")
    description=models.CharField("Description",blank=True,null=True,max_length=128)
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)
##
##
##
class VRF(models.Model):
    class Meta:
        verbose_name="VRF"
        verbose_name_plural="VRFs"
    name=models.CharField("VRF name",unique=True,max_length=64)
    vrf_group=models.ForeignKey(VRFGroup,verbose_name="VRF Group")
    rd=models.CharField("rd",unique=True,max_length=21) # validator_list=[check_rd],
    description=models.CharField("Description",blank=True,null=True,max_length=128)
    tt=models.IntegerField("TT",blank=True,null=True)
    def __str__(self):
        if self.rd=="0:0":
            return "global"
        return self.rd
    def __unicode__(self):
        if self.rd=="0:0":
            return u"global"
        return self.rd
        
    def prefix(self,top="0.0.0.0/0"):
        assert is_cidr(top)
        return IPv4Block.objects.get(prefix=top,vrf=self)
        
    def prefixes(self,top="0.0.0.0/0"):
        assert is_cidr(top)
        return self.prefix(top).children
        
    def all_prefixes(self,top="0.0.0.0/0"):
        assert is_cidr(top)
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d and prefix<<='%s' order by prefix"%(IPv4Block._meta.db_table,self.id,top))
        return [IPv4Block.objects.get(id=x[0]) for x in c.fetchall()]
        
    def all_addresses(self,top="0.0.0.0/0"):
        assert is_cidr(top)
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d and ip<<='%s' order by ip"%(IPv4Address._meta.db_table,self.id,top))
        return [IPv4Address.objects.get(id=x[0]) for x in c.fetchall()]
##
##
##
class IPv4BlockAccess(models.Model):
    class Meta:
        verbose_name="IPv4 Block Access"
        verbose_name_plural="IPv4 Block Access"
        unique_together=[("user","vrf","prefix")]
    user=models.ForeignKey(User,verbose_name="User")
    vrf=models.ForeignKey(VRF,verbose_name="VRF")
    prefix=CIDRField("prefix")
    tt=models.IntegerField("TT",blank=True,null=True)
    def __str__(self):
        return "%s: %s(%s)"%(self.user,self.prefix,self.vrf)
    @classmethod
    def check_write_access(self,user,vrf,prefix):
        assert is_cidr(prefix)
        if user.is_superuser:
            return True
        c=connection.cursor()
        c.execute("SELECT COUNT(*) FROM %s WHERE prefix >>= '%s' AND vrf_id=%d AND user_id=%d"%(IPv4BlockAccess._meta.db_table,str(prefix),vrf.id,user.id))
        return c.fetchall()[0][0]>0
##
##
##
class IPv4Block(models.Model):
    class Meta:
        verbose_name="IPv4 Block"
        verbose_name_plural="IPv4 Blocks"
        unique_together=[("prefix","vrf")]
        ordering=["prefix"]
    description=models.CharField("Description",max_length=64)
    prefix=CIDRField("prefix")
    vrf=models.ForeignKey(VRF)
    asn=models.ForeignKey(AS)
    vc=models.ForeignKey(VC,verbose_name="VC",null=True,blank=True)
    modified_by=models.ForeignKey(User,verbose_name="User")
    last_modified=models.DateTimeField("Last modified",auto_now=True,auto_now_add=True)
    tt=models.IntegerField("TT",blank=True,null=True)
    #allocated_till
    def __str__(self):
        return str(self.prefix)
    def __unicode__(self):
        return unicode(self.prefix)
    def _parent(self):
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE prefix >> '%s' AND vrf_id=%d ORDER BY masklen(prefix) DESC LIMIT 1"%(IPv4Block._meta.db_table,
                    self.prefix,self.vrf.id))
        r=c.fetchall()
        if len(r)==0:
            return
        return IPv4Block.objects.get(id=r[0][0])
    parent=property(_parent)

    def _parents(self):
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE prefix >> '%s' AND vrf_id=%d ORDER BY masklen(prefix)"%(IPv4Block._meta.db_table,
                    self.prefix,self.vrf.id))
        return [IPv4Block.objects.get(id=i[0]) for i in c.fetchall()]
    parents=property(_parents)

    def _depth(self):
        c=connection.cursor()
        c.execute("SELECT COUNT(*) FROM %s WHERE prefix >> '%s' AND vrf_id=%d"%(IPv4Block._meta.db_table,self.prefix,self.vrf.id))
        return c.fetchone()[0]
    depth=property(_depth)

    def _children(self):
        c=connection.cursor()
        if self.vrf.vrf_group.unique_addresses:
            vrfs="IN (%s)"%",".join([str(vrf.id) for vrf in self.vrf.vrf_group.vrf_set.all()])
            vg_id=self.vrf.vrf_group.id
            c.execute("SELECT b.id FROM %s b JOIN %s v ON (b.vrf_id=v.id) WHERE b.prefix << '%s' AND v.id %s AND ip_ipv4_block_depth_in_vrf_group(%d,b.prefix,'%s')=0 ORDER BY prefix"%\
                        (IPv4Block._meta.db_table,VRF._meta.db_table,self.prefix,vrfs,vg_id,self.prefix))
        else:
            vrfs="= %d"%self.vrf.id
            c.execute("SELECT b.id FROM %s b JOIN %s v ON (b.vrf_id=v.id) WHERE b.prefix << '%s' AND v.id %s AND ip_ipv4_block_depth(v.id,b.prefix,'%s')=0 ORDER BY prefix"%\
                        (IPv4Block._meta.db_table,VRF._meta.db_table,self.prefix,vrfs,self.prefix))
        return [IPv4Block.objects.get(id=i[0]) for i in c.fetchall()]

    children=property(_children)

    def _has_children(self):
        c=connection.cursor()
        if self.vrf.vrf_group.unique_addresses:
            vrfs="IN (%s)"%",".join([str(vrf.id) for vrf in self.vrf.vrf_group.vrf_set.all()])
        else:
            vrfs="= %d"%self.vrf.id
        data=[]
        c.execute("SELECT COUNT(*) FROM %s b JOIN %s v ON (b.vrf_id=v.id) WHERE b.prefix << '%s' AND v.id %s AND ip_ipv4_block_depth(v.id,b.prefix,'%s')=0"%\
                    (IPv4Block._meta.db_table,VRF._meta.db_table,self.prefix,vrfs,self.prefix))
        return c.fetchall()[0][0]>0
    has_children=property(_has_children)

    def _addresses(self):
        if self.has_children:
            return []
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d AND ip <<= '%s' ORDER BY ip"%(IPv4Address._meta.db_table,self.vrf.id,self.prefix))
        return [IPv4Address.objects.get(id=i[0]) for i in c.fetchall()]
    addresses=property(_addresses)
    ##
    ## Return number of allocated addresses
    ##
    def _address_count(self):
        if self.has_children:
            return []
        c=connection.cursor()
        c.execute("SELECT COUNT(*) FROM ip_ipv4address WHERE vrf_id=%s AND ip << %s::cidr",[self.vrf.id,self.prefix])
        return c.fetchall()[0][0]
    address_count=property(_address_count)
    ##
    ## Return IP addresses not belonging to any subblocks
    ##
    def _orphaned_addresses(self):
        children=self.children
        if not children:
            return []
        x=" OR ".join(["(ip <<= '%s')"%c.prefix for c in children])
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d AND ip <<= '%s' AND NOT (%s) ORDER BY ip"%(IPv4Address._meta.db_table,self.vrf.id,self.prefix,x))
        return [IPv4Address.objects.get(id=i[0]) for i in c.fetchall()]
    orphaned_addresses=property(_orphaned_addresses)
        
    ##
    ## Generator returning a nested ip addresses (including nested children)
    ##
    def _nested_addresses(self):
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d AND ip << '%s' ORDER BY ip"%(IPv4Address._meta.db_table,self.vrf.id,self.prefix))
        for row in c:
            yield IPv4Address.objects.get(id=row[0])
    nested_addresses=property(_nested_addresses)
    ##
    ## Return a list of all used/unused addresses
    ##
    def _all_addresses(self):
        if self.has_children:
            return None
        a=dict((x.ip,x) for x in self.addresses)
        if len(a)==0:
            return []
        r=[]
        for nip in range(address_to_int(self.network),address_to_int(self.broadcast)+1):
            ip=int_to_address(nip)
            if ip in a:
                r.append(a[ip])
            else:
                r.append(ip)
        return r
    all_addresses=property(_all_addresses)
    ##
    ## Returns a list of responsible persons with write permissions
    ##
    def _maintainers(self):
        c=connection.cursor()
        c.execute("SELECT id FROM auth_user WHERE is_active=True AND (is_superuser=True OR id IN (SELECT user_id FROM ip_ipv4blockaccess WHERE vrf_id=%s AND prefix>>=%s)) ORDER BY username",
            [self.vrf.id,self.prefix])
        for user_id, in c:
            yield User.objects.get(id=user_id)
    maintainers=property(_maintainers)

    def _netmask_bits(self):
        return int(str(self.prefix).split("/")[1])
    netmask_bits=property(_netmask_bits)

    def _netmask(self):
        return int_to_address(bits_to_int(self.netmask_bits))
    netmask=property(_netmask)

    def _network(self):
        return str(self.prefix).split("/")[0]
    network=property(_network)

    def _wildcard(self): 
        return wildcard(self.prefix)
    wildcard=property(_wildcard)

    def _broadcast(self):
        return broadcast(self.prefix)
    broadcast=property(_broadcast)
    ##
    ## Block size in IP addresses
    ##
    def _size(self):
        return prefix_to_size(self.prefix)
    size=property(_size)
    
    def _tt_url(self):
        return tt_url(self)
    tt_url=property(_tt_url)
    ##
    ## A list of block's ranges
    ##
    def _ranges(self):
        if self.has_children:
            return []
        c=connection.cursor()
        c.execute("SELECT id FROM ip_ipv4addressrange WHERE vrf_id=%s AND %s::cidr>>from_ip AND %s::cidr>>to_ip",
            [self.vrf.id,self.prefix,self.prefix])
        ids=[x[0] for x in c.fetchall()]
        return IPv4AddressRange.objects.filter(id__in=ids)
    ranges=property(_ranges)
    ##
    ## Search engine plugin
    ##
    @classmethod
    def search(cls,user,search,limit):
        if user.has_perm("ip.change_ipv4block"):
            q=Q(description__icontains=search)
            if is_cidr(search):
                q|=Q(prefix=search)
            for r in IPv4Block.objects.filter(q):
                if search==r.prefix:
                    relevancy=1.0
                else:
                    l=len(r.description)
                    if l:
                        relevancy=float(len(search))/float(l)
                    else:
                        relevancy=0.0
                yield SearchResult(url="/ip/%d/%s/"%(r.vrf.id,r.prefix),
                    title="IPv4 Block, VRF=%s, %s"%(r.vrf,r.prefix),
                    text=r.description,
                    relevancy=relevancy)
##
## IPv4 Address Range
##
rx_var=re.compile(r"\{\{([^}]+)\}\}")
class IPv4AddressRange(models.Model):
    class Meta:
        verbose_name="IPv4 Address Range"
        verbose_name_plural="IPv4 Address Ranges"
        unique_together=[("vrf","name")]
    vrf=models.ForeignKey(VRF,verbose_name="VRF")
    name=models.CharField("Name",max_length=64)
    from_ip=models.IPAddressField("From IP")
    to_ip=models.IPAddressField("To Address")
    description=models.TextField("Description",null=True,blank=True)
    is_locked=models.BooleanField("Range is locked",default=False) # Deny manual IPv4Address editing
    fqdn_action=models.CharField("FQDN Action",max_length=1,choices=[("N","Do Nothing"),("G","Generate FQDN"),("D","Delegate Reverse zone")],default="N")
    fqdn_action_parameter=models.CharField("FQDN Action Parameter",max_length=128,null=True,blank=True)
    def __unicode__(self):
        return u"%s (%s:%s-%s)"%(self.name,self.vrf.name,self.from_ip,self.to_ip)
    ##
    ## Find Matching range
    ## Returns range object or None
    ##
    @classmethod
    def get_range(cls,vrf,ip):
        c=connection.cursor()
        c.execute("SELECT id FROM ip_ipv4addressrange WHERE vrf_id=%s AND %s::inet BETWEEN from_ip AND to_ip",[vrf.id,ip])
        r=c.fetchall()
        if r:
            return IPv4AddressRange.objects.get(id=r[0][0])
        else:
            return None
    ##
    ## Generator returning all ip addresses in range
    ##
    def _addresses(self):
        for ip in generate_ips(self.from_ip,self.to_ip):
            yield ip
    addresses=property(_addresses)
    ##
    ## Check for range overlap
    ## Returns a list of overlapping ranges
    ##
    @classmethod
    def get_range_overlap(cls,vrf,from_ip,to_ip,instance=None):
        c=connection.cursor()
        SQL="""SELECT id FROM ip_ipv4addressrange WHERE vrf_id=%s AND from_ip<=%s::inet AND to_ip>=%s::inet """
        P=[vrf.id,to_ip,from_ip]
        if instance:
            SQL+=" AND id!=%s"
            P+=[instance.id]
        c.execute(SQL,P)
        return IPv4AddressRange.objects.filter(id__in=[x[0] for x in c.fetchall()])
            
    ##
    ## Check for overlapping IPv4 blocks overlap
    ## Returns a list of overlapping IPv4 Blocks
    ##
    @classmethod
    def get_block_overlap(cls,vrf,from_ip,to_ip):
        c=connection.cursor()
        c.execute("""SELECT id FROM ip_ipv4block
                WHERE vrf_id=%s
                    AND (
                        (prefix >> %s::inet AND NOT (prefix >> %s::inet))
                        OR (prefix >> %s::inet AND NOT (prefix >> %s::inet))
                        )""",
            [vrf.id,from_ip,to_ip,to_ip,from_ip])
        return IPv4Block.objects.filter(id__in=[x[0] for x in c.fetchall()])
    ##
    ## Check IP address falls into locked range
    ##
    @classmethod
    def is_range_locked(cls,vrf,ip):
        r=cls.get_range(vrf,ip)
        if r:
            return r.is_locked
        else:
            return False
    ##
    ## Generate reverse zone delegation for DNS provisioning
    ##
    
    ##
    ## Expand FQDN for ip
    ##
    ## Variables are:
    ## {{ip1}},{{ip2}},{{ip2}},{{ip4}} - first, second, third and fourth octets (decimal)
    ##
    def expand_fqdn(self,ip):
        if self.fqdn_action!="G" and not self.fqdn_action_parameter:
            return None
        ip1,ip2,ip3,ip4=ip.split(".")
        vars={
            "ip1" : ip1,
            "ip2" : ip2,
            "ip3" : ip3,
            "ip4" : ip4,
        }
        return rx_var.sub(lambda x:vars.get(x.group(1),""),self.fqdn_action_parameter)
    ##
    ##
    ##
    def sync_fqdns(self):
        if self.fqdn_action!="G":
            return
        # Generate IP addresses
        user=get_user()
        for ip in self.addresses:
            try:
                i=IPv4Address.objects.get(vrf=self.vrf,ip=ip)
                i.fqdn=self.expand_fqdn(ip)
                i.description="Generated by IP address range: %s"%self.name
                i.modified_by=user
                i.save()
            except IPv4Address.DoesNotExist:
                IPv4Address(vrf=self.vrf,
                    fqdn=self.expand_fqdn(ip),
                    ip=ip,
                    description="Generated by IP address range: %s"%self.name,
                    modified_by=user).save()
    ##
    ##
    ##
    def save(self,**kwargs):
        # Check parameters
        if self.is_locked==False and self.fqdn_action!="N":
            raise ValueError("FQDN Action requires locked range")
        if self.fqdn_action in ["G","D"] and not self.fqdn_action_parameter:
            raise ValueError("FQDN Action Paratemer required")
        # Sync generated addresses
        is_new=self.id is None
        if not is_new:
            old=IPv4AddressRange.objects.get(id=self.id)
        super(IPv4AddressRange,self).save(**kwargs)
        if is_new:
            if self.fqdn_action=="G":
                # Generate FQDNs
                self.sync_fqdns()
        else:
            if old.fqdn_action=="G" and self.fqdn_action!="G":
                # Drop auto-generated IPs
                for i in IPv4Address.get_addresses(self.vrf,self.from_ip,self.to_ip):
                    i.delete()
            elif old.fqdn_action!="G" and self.fqdn_action=="G":
                # Generate FQDNs
                self.sync_fqdns()
            elif self.fqdn_action=="G":
                if old.from_ip<self.from_ip:
                    # Delete IP addresses that falls out of range
                    for i in IPv4Address.get_addresses(self.vrf,old.from_ip,self.from_ip):
                        i.delete()
                if old.to_ip>self.to_ip:
                    # Delete IP addresses that falls out of range
                    for i in IPv4Address.get_addresses(self.vrf,self.to_ip,old.to_ip):
                        i.delete()
                self.sync_fqdns()
##
##
##
class IPv4Address(models.Model):
    class Meta:
        unique_together=[("vrf","ip")]
        verbose_name="IPv4 Address"
        verbose_name_plural="IPv4 Addresses"
        ordering=["ip"]
    vrf=models.ForeignKey(VRF,verbose_name="VRF")
    fqdn=models.CharField("FQDN",max_length=64)
    ip=models.IPAddressField("IP")
    description=models.CharField("Description",blank=True,null=True,max_length=64)
    modified_by=models.ForeignKey(User,verbose_name="User")
    last_modified=models.DateTimeField("Last modified",auto_now=True,auto_now_add=True)
    tt=models.IntegerField("TT",blank=True,null=True)
    
    def __unicode__(self):
        return self.ip

    def __str__(self):
        return self.ip

    def _parent(self):
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d AND '%s' << prefix ORDER BY masklen(prefix) DESC LIMIT 1"%(IPv4Block._meta.db_table,self.vrf.id,str(self.ip)))
        return IPv4Block.objects.get(id=c.fetchall()[0][0])
    parent=property(_parent)
    
    def _tt_url(self):
        return tt_url(self)
    tt_url=property(_tt_url)
    ##
    ## All IPv4Address objects in range
    ##
    @classmethod
    def get_addresses(self,vrf,from_ip,to_ip):
        c=connection.cursor()
        SQL="SELECT id FROM ip_ipv4address WHERE vrf_id=%s AND ip BETWEEN %s::inet AND %s::inet ORDER BY ip"
        c.execute(SQL,[vrf.id,from_ip,to_ip])
        return IPv4Address.objects.filter(id__in=[x[0] for x in c.fetchall()])
    ##
    ## Search engine
    ##
    @classmethod
    def search(cls,user,search,limit):
        if user.has_perm("ip.change_ipv4address"):
            q=Q(fqdn__icontains=search)|Q(description__icontains=search)
            if is_ipv4(search):
                q|=Q(ip=search)
            for r in IPv4Address.objects.filter(q):
                if search==r.ip:
                    relevancy=1.0
                else:
                    ls=float(len(search))
                    if search in r.fqdn and len(r.fqdn)>0:
                        r_fqdn=ls/float(len(r.fqdn))
                    else:
                        r_fqdn=0.0
                    if r.description and search in r.description and len(r.description)>0:
                        r_description=ls/float(len(r.description))
                    else:
                        r_description=0.0
                    relevancy=max(r_fqdn,r_description)
                yield SearchResult(url="/ip/%d/%s/assign_address/"%(r.vrf.id,r.ip),
                    title="IPv4 Address, VRF=%s, %s (%s)"%(r.vrf,r.ip,r.fqdn),
                    text=r.description,
                    relevancy=relevancy)
##
## Application Menu
##
class AppMenu(Menu):
    app="ip"
    title="Address Space Management"
    items=[
        ("Assigned addresses", "/ip/", "ip.change_ipv4block"),
        ("Setup",[
            ("VRF Groups",  "/admin/ip/vrfgroup/",        "ip.change_vrfgroup"),
            ("VRFs",        "/admin/ip/vrf/",             "ip.change_vrf"),
            ("Block Access","/admin/ip/ipv4blockaccess/", "ip.change_ipv4blockaccess"),
            ("IPv4 Address Ranges","/admin/ip/ipv4addressrange/", "ip.change_ipv4addressrange"),
            ]
        )
    ]
