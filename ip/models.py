##
## This file is a part of Effortel's NOC db project
##
from django.db import models
from django.contrib.auth.models import User
from noc.lib.validators import check_rd,check_cidr,is_cidr
from noc.asn.models import AS

##
##
##
class VRFGroup(models.Model):
    class Admin:
        list_display=["name","unique_addresses"]
        search_fields=["name"]
    class Meta:
        verbose_name="VRF Group"
        verbose_name_plural="VRF Groups"
    name=models.CharField("VRF Group",unique=True,maxlength=64)
    unique_addresses=models.BooleanField("Unique addresses in group")
    def __str__(self):
        return self.name
    def __unicode__(self):
        return unicode(self.name)
##
##
##
class VRF(models.Model):
    class Admin:
        list_display=["rd","name","vrf_group"]
        search_fields=["name","rd"]
        list_filter=["vrf_group"]
    class Meta:
        verbose_name="VRF"
        verbose_name_plural="VRFs"
    name=models.CharField("VRF name",unique=True,maxlength=64)
    vrf_group=models.ForeignKey(VRFGroup,verbose_name="VRF Group")
    rd=models.CharField("rd",unique=True,validator_list=[check_rd],maxlength=21)
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
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d and prefix_cidr<<='%s' order by prefix_cidr"%(IPv4Block._meta.db_table,self.id,top))
        return [IPv4Block.objects.get(id=x[0]) for x in c.fetchall()]
        
    def all_addresses(self,top="0.0.0.0/0"):
        assert is_cidr(top)
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d and ip<<='%s' order by ip"%(IPv4Address._meta.db_table,self.id,top))
        return [IPv4Address.objects.get(id=x[0]) for x in c.fetchall()]
##
##
##
class IPv4BlockAccess(models.Model):
    class Admin:
        list_display=["user","vrf","prefix"]
        list_filter=["user","vrf"]
        search_fields=["user","prefix"]
    class Meta:
        verbose_name="IPv4 Block Access"
        verbose_name_plural="IPv4 Block Access"
        unique_together=[("user","vrf","prefix")]
    user=models.ForeignKey(User,verbose_name="User")
    vrf=models.ForeignKey(VRF,verbose_name="VRF")
    prefix=models.CharField("prefix",maxlength=18)
    def __str__(self):
        return "%s: %s(%s)"%(self.user,self.prefix,self.vrf)
    @classmethod
    def check_write_access(self,user,vrf,prefix):
        from django.db import connection
        if user.is_superuser:
            return True
        c=connection.cursor()
        c.execute("SELECT COUNT(*) FROM %s WHERE prefix_cidr >>= '%s' AND vrf_id=%d AND user_id=%d"%(IPv4BlockAccess._meta.db_table,str(prefix),vrf.id,user.id))
        return c.fetchall()[0][0]>0
##
##
##
class IPv4Block(models.Model):
    class Admin:
        list_display=["prefix","vrf","description"]
        list_filter=["vrf","asn"]
        search_fields=["prefix","description"]
    class Meta:
        verbose_name="IPv4 Block"
        verbose_name_plural="IPv4 Blocks"
        unique_together=[("prefix","vrf")]
        ordering=["prefix"]
    description=models.CharField("Description",maxlength=64)
    prefix=models.CharField("prefix",maxlength=18)
    vrf=models.ForeignKey(VRF)
    asn=models.ForeignKey(AS)
    modified_by=models.ForeignKey(User,verbose_name="User")
    last_modified=models.DateTimeField("Last modified",auto_now=True,auto_now_add=True)
    def __str__(self):
        return str(self.prefix)
    def __unicode__(self):
        return unicode(self.prefix)
    def _parent(self):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE prefix_cidr >> '%s' AND vrf_id=%d ORDER BY masklen(prefix_cidr) DESC LIMIT 1"%(IPv4Block._meta.db_table,
                    self.prefix,self.vrf.id))
        r=c.fetchall()
        if len(r)==0:
            return
        return IPv4Block.objects.get(id=r[0][0])
    parent=property(_parent)

    def _parents(self):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE prefix_cidr >> '%s' AND vrf_id=%d ORDER BY masklen(prefix_cidr)"%(IPv4Block._meta.db_table,
                    self.prefix,self.vrf.id))
        return [IPv4Block.objects.get(id=i[0]) for i in c.fetchall()]
    parents=property(_parents)

    def _depth(self):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT COUNT(*) FROM %s WHERE prefix_cidr >> '%s' AND vrf_id=%d"%(IPv4Block._meta.db_table,self.prefix,self.vrf.id))
        return c.fetchone()[0]
    depth=property(_depth)

    def _children(self):
        from django.db import connection
        c=connection.cursor()
        if self.vrf.vrf_group.unique_addresses:
            vrfs="IN (%s)"%",".join([str(vrf.id) for vrf in self.vrf.vrf_group.vrf_set.all()])
        else:
            vrfs="= %d"%self.vrf.id
        data=[]
        c.execute("SELECT b.id FROM %s b JOIN %s v ON (b.vrf_id=v.id) WHERE b.prefix_cidr << '%s' AND v.id %s AND ip_ipv4_block_depth(v.id,b.prefix_cidr,'%s')=0 ORDER BY prefix_cidr"%\
                    (IPv4Block._meta.db_table,VRF._meta.db_table,self.prefix,vrfs,self.prefix))
        return [IPv4Block.objects.get(id=i[0]) for i in c.fetchall()]
    children=property(_children)

    def _has_children(self):
        from django.db import connection
        c=connection.cursor()
        if self.vrf.vrf_group.unique_addresses:
            vrfs="IN (%s)"%",".join([str(vrf.id) for vrf in self.vrf.vrf_group.vrf_set.all()])
        else:
            vrfs="= %d"%self.vrf.id
        data=[]
        c.execute("SELECT COUNT(*) FROM %s b JOIN %s v ON (b.vrf_id=v.id) WHERE b.prefix_cidr << '%s' AND v.id %s AND ip_ipv4_block_depth(v.id,b.prefix_cidr,'%s')=0 ORDER BY prefix_cidr"%\
                    (IPv4Block._meta.db_table,VRF._meta.db_table,self.prefix,vrfs,self.prefix))
        return c.fetchall()[0][0]>0
    has_children=property(_has_children)

    def _addresses(self):
        if self.has_children:
            return None
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d AND ip << '%s' ORDER BY ip"%(IPv4Block._meta.db_table,self.vrf.id,self.prefix))
        return [IPv4Address.objects.get(id=i[0]) for i in c.fetchall()]
    addresses=property(_addresses)

    def __get_ip(self,ip):
        return socket.inet_ntoa(struct.pack("!L",ip))
    def __mask_for_bits(self,bits):
        return ((1L<<bits)-1L)<<(32L-bits)
    def __get_ip_bits(self,ip):
        return struct.unpack("!L",socket.inet_aton(ip))[0]

    def _netmask_bits(self):
        return int(str(self.prefix).split("/")[1])
    netmask_bits=property(_netmask_bits)

    def _netmask(self):
        return self.__get_ip(self.__mask_for_bits(self.netmask_bits))
    netmask=property(_netmask)

    def _network(self):
        return str(self.prefix).split("/")[0]
    network=property(_network)

    def _wildcard(self): 
        return self.__get_ip(0xFFFFFFFFL^self.__mask_for_bits(self.netmask_bits))
    wildcard=property(_wildcard)

    def _broadcast(self):
        return self.__get_ip(self.__get_ip_bits(str(self.prefix).split("/")[0])|(0xFFFFFFFFL^self.__mask_for_bits(self.netmask_bits)))
    broadcast=property(_broadcast)

##
##
##
class IPv4Address(models.Model):
    class Admin:
        list_display=["ip","fqdn","vrf","description"]
        list_filter=["vrf"]
        search_fields=["ip","fqdn","description"]
    class Meta:
        unique_together=[("vrf","ip")]
        verbose_name="IPv4 Address"
        verbose_name_plural="IPv4 Addresses"
        ordering=["ip"]
    vrf=models.ForeignKey(VRF,verbose_name="VRF")
    fqdn=models.CharField("FQDN",maxlength=64)
    ip=models.IPAddressField("IP")
    description=models.CharField("Description",blank=True,null=True,maxlength=64)
    modified_by=models.ForeignKey(User,verbose_name="User")
    last_modified=models.DateTimeField("Last modified",auto_now=True,auto_now_add=True)

    def __unicode__(self):
        return self.ip

    def __str__(self):
        return self.ip

    def _closest_block(self):
        from django.db import connection
        c=connection.cursor()
        c.execute("SELECT id FROM %s WHERE vrf_id=%d AND '%s' << prefix_cidr ORDER BY masklen(prefix_cidr) DESC LIMIT 1"%(IPv4Block._meta.db_table,self.vrf.id,str(self.ip)))
        return IPv4Block.objects.get(id=c.fetchall()[0][0])
    closest_block=property(_closest_block)