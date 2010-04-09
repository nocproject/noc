# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django's standard models module
## For VC application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.db import models,connection
from django.db.models import Q
from noc.main.menu import Menu
from noc.main.search import SearchResult
from noc.main.models import NotificationGroup
from noc.sa.models import ManagedObjectSelector
from noc.lib.validators import is_int
from noc.lib.fields import CIDRField
import re
##
## VC Type
##
class VCType(models.Model):
    class Meta:
        verbose_name="VC Type"
        verbose_name_plural="VC Types"
    name=models.CharField("Name",max_length=32,unique=True)
    min_labels=models.IntegerField("Min. Labels",default=1)
    label1_min=models.IntegerField("Label1 min")
    label1_max=models.IntegerField("Label1 max")
    label2_min=models.IntegerField("Label2 min",null=True,blank=True)
    label2_max=models.IntegerField("Label2 max",null=True,blank=True)
    def __unicode__(self):
        return self.name
##
## Virtual circuit domain, allows to separate unique VC spaces
##
class VCDomain(models.Model):
    class Meta:
        verbose_name="VC Domain"
        verbose_name_plural="VC Domains"
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",blank=True,null=True)
    type=models.ForeignKey(VCType,verbose_name="Type")
    enable_provisioning=models.BooleanField("Enable Provisioning",default=False)
    enable_vc_bind_filter=models.BooleanField("Enable VC Bind filter",default=False)
    def __unicode__(self):
        return u"%s: %s"%(self.name,unicode(self.type))
##
## VC Filter
##
rx_vc_filter=re.compile(r"^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$")
class VCFilter(models.Model):
    class Meta:
        verbose_name="VC Filter"
        verbose_name_plural="VC Filters"
        ordering=["name"]
    name=models.CharField("Name",max_length=64,unique=True)
    expression=models.CharField("Expression",max_length=256)
    description=models.TextField("Description",null=True,blank=True)
    def __unicode__(self):
        return self.name
    ##
    ## Compile VC Filter expression
    ##
    @classmethod
    def compile(self,expression):
        if not rx_vc_filter.match(expression):
            raise SyntaxError
        r=[]
        for x in expression.split(","):
            x=x.strip()
            if "-" in x:
                f,t=[int(c.strip()) for c in x.split("-")]
            else:
                f=int(x)
                t=f
            if t<f:
                raise SyntaxError
            r+=[(f,t)]
        return r
    ##
    ## Check filter matches VC
    ##
    def check(self,vc):
        if not hasattr(self,"_compiled_expression"):
            self._compiled_expression=VCFilter.compile(self.expression)
        for f,t in self._compiled_expression:
            if f<=vc<=t:
                return True
        return False
    ##
    ## Link to test filter
    ##
    def test_link(self):
        return "<a href='/vc/vcfilter/%d/test/'>Test</a>"%self.id
    test_link.short_description="Test VC Filter"
    test_link.allow_tags=True
##
##
##
class VCBindFilter(models.Model):
    class Meta:
        verbose_name="VC Bind Filter"
        verbose_name_plural="VC Bind Filters"
    vc_domain=models.ForeignKey(VCDomain,verbose_name="VC Domain")
    vrf=models.ForeignKey("ip.VRF",verbose_name="VRF")
    prefix=CIDRField("prefix")
    vc_filter=models.ForeignKey(VCFilter,verbose_name="VC Filter")
    def __unicode__(self):
        return "%s %s %s %s"%(self.vc_domain,self.vrf,self.prefix,self.vc_filter)
    #
    @classmethod
    def get_choices(cls,prefix):
        r=list(VC.objects.filter(vc_domain__in=[d.id for d in VCDomain.objects.filter(enable_vc_bind_filter=False)]))
        for d in VCDomain.objects.filter(enable_vc_bind_filter=True):
            cursor=connection.cursor()
            cursor.execute("""SELECT DISTINCT vc_filter_id
            FROM vc_vcbindfilter
            WHERE vc_domain_id=%s
                AND vrf_id=%s
                AND prefix>>=%s::inet
            """,[d.id,prefix.vrf.id,prefix.prefix])
            filters=[VCFilter.objects.get(id=f_id) for f_id, in cursor.fetchall()]
            for vc in d.vc_set.all():
                for f in filters:
                    if f.check(vc.l1):
                        r+=[vc]
        r=sorted(r,lambda x,y:cmp(x.l1,y.l1))
        return [(o.id,unicode(o)) for o in r]

##
## VCDomain Provisioning Parameters
##
class VCDomainProvisioningConfig(models.Model):
    class Meta:
        verbose_name="VC Domain Provisioning Config"
        verbose_name_plural="VC Domain Provisioning Config"
        unique_together=[("vc_domain","selector")]
    vc_domain=models.ForeignKey(VCDomain,verbose_name="VC Domain")
    selector=models.ForeignKey(ManagedObjectSelector,verbose_name="Managed Object Selector")
    is_enabled=models.BooleanField("Is Enabled",default=True)
    vc_filter=models.ForeignKey(VCFilter,verbose_name="VC Filter",null=True,blank=True)
    tagged_ports=models.CharField("Tagged Ports",max_length=256,null=True,blank=True)
    notification_group=models.ForeignKey(NotificationGroup,verbose_name="Notification Group",null=True,blank=True)    
    def __unicode__(self):
        return u"%s: %s"%(unicode(self.vc_domain),unicode(self.selector))
    ##
    ## Returns a list of tagged ports
    ##
    def _tagged_ports_list(self):
        if self.tagged_ports:
            return [x.strip() for x in self.tagged_ports.split(",")]
        else:
            return []
    tagged_ports_list=property(_tagged_ports_list)
##
## Virtual circuit
##
rx_vc_underline=re.compile("\s+")
rx_vc_empty=re.compile(r"[^a-zA-Z0-9\-_]+")
class VC(models.Model):
    class Meta:
        verbose_name="VC"
        verbose_name_plural="VCs"
        unique_together=[("vc_domain","l1","l2"),("vc_domain","name")]
        ordering=["vc_domain","l1","l2"]
    vc_domain=models.ForeignKey(VCDomain,verbose_name="VC Domain")
    name=models.CharField("Name",max_length=64)
    l1=models.IntegerField("Label 1")
    l2=models.IntegerField("Label 2",default=0)
    description=models.CharField("Description",max_length=256,null=True,blank=True)

    def __unicode__(self):
        s=u"%s %d"%(self.vc_domain,self.l1)
        if self.l2:
            s+=u"/%d"%self.l2
        s+=u": %s"%self.name
        return s
    ##
    ##
    ##
    def blocks_list(self):
        return ", ".join([p.prefix for p in self.ipv4block_set.order_by("prefix")])
    blocks_list.short_description="Blocks"
    blocks_list.allow_tags=False
    ##
    ## Enforce additional checks
    ##
    def save(self):
        if self.l1<self.vc_domain.type.label1_min or self.l1>self.vc_domain.type.label1_max:
            raise Exception("Invalid value for L1")
        if self.vc_domain.type.min_labels>1 and not self.l2:
            raise Exception("L2 required")
        if self.vc_domain.type.min_labels>1 and not (self.l2>=self.vc_domain.type.label2_min and self.l2<=self.vc_domain.type.label2_max):
            raise Exception("Invalid value for L2")
        # Format name
        if self.name:
            name=rx_vc_underline.sub("_",self.name)
            name=rx_vc_empty.sub("",name)
            self.name=name
        else:
            self.name="VC_%04d"%self.l1
        super(VC,self).save()
    ##
    ## Search engine
    ##
    @classmethod
    def search(cls,user,search,limit):
        if user.has_perm("vc.change_vc"):
            if is_int(search):
                tag=int(search)
                for r in VC.objects.filter(Q(l1=tag)|Q(l2=tag))[:limit]:
                    if r.l2:
                        label="%d,%d"%(r.l1,r.l2)
                    else:
                        label="%d"%r.l1
                    yield SearchResult(url="/admin/vc/vc/%d/"%r.id,
                        title="VC: %s, Domain: %s, Label=%s"%(r.type,r.vc_domain.name,label),
                        text=r.description,
                        relevancy=1.0)
##
## Application Menu
##
class AppMenu(Menu):
    app="vc"
    title="Virtual Circuit Management"
    items=[
        ("Virtual Circuits", "/admin/vc/vc/", "vc.change_vc"),
        ("Setup",[
            ("VC Domains", "/admin/vc/vcdomain/", "vc.change_vcdomain"),
            ("VC Filters", "/admin/vc/vcfilter/", "vc.change_vcfilter"),
            ("VC Bind Filters", "/admin/vc/vcbindfilter/", "vc.change_vcbindfilter"),
            ("VC Types",   "/admin/vc/vctype/", "vc.change_vctype"),
        ])
    ]
