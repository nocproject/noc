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
from django.db import models
from django.db.models import Q
from noc.main.menu import Menu
from noc.main.search import SearchResult
from noc.lib.validators import is_int
##
## Virtual circuit domain, allows to separate unique VC spaces
##
class VCDomain(models.Model):
    class Meta:
        verbose_name="VC Domain"
        verbose_name_plural="VC Domains"
    name=models.CharField("Name",max_length=64,unique=True)
    description=models.TextField("Description",blank=True,null=True)
    
    def __unicode__(self):
        return self.name
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
## Virtual circuit
##
class VC(models.Model):
    class Meta:
        verbose_name="VC"
        verbose_name_plural="VCs"
        unique_together=[("vc_domain","type","l1","l2")]
    vc_domain=models.ForeignKey(VCDomain,verbose_name="VC Domain")
    type=models.ForeignKey(VCType,verbose_name="type")
    l1=models.IntegerField("Label 1")
    l2=models.IntegerField("Label 2",default=0)
    description=models.CharField("Description",max_length=256)

    def __unicode__(self):
        s=u"%s %s %d"%(self.vc_domain,self.type,self.l1)
        if self.l2:
            s+=u"/%d"%self.l2
        return s
    ##
    ## Enforce additional checks
    ##
    def save(self):
        if self.l1<self.type.label1_min or self.l1>self.type.label1_max:
            raise Exception("Invalid value for L1")
        if self.type.min_labels>1 and not self.l2:
            raise Exception("L2 required")
        if self.type.min_labels>1 and not (self.l2>=self.type.label2_min and self.l2<=self.type.label2_max):
            raise Exception("Invalid value for L2")
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
            ("VC Types",   "/admin/vc/vctype/", "vc.change_vctype"),
        ])
    ]
