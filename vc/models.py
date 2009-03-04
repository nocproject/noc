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
from noc.main.menu import Menu

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
## Virtual circuit checks
## type -> (name, min labels, l1range, l2range)
## where l1/l2 ranges are tuples of (min,max) or None
##
vc_checks={
    "q": ("802.1Q VLAN",        1, (1,4095),     None),
    "Q": ("802.1ad Q-in-Q",     2, (1,4095),     (1,4095)),
    "D": ("FR DLCI",            1, (16,991),     None),
    "M": ("MPLS",               1, (16,1048575), (16,1048575)),
    "A": ("ATM VCI/VPI",        1, (0,65535),    (0,4095)),
    "X": ("X.25 group/channel", 2, (0,15),       (0,255)),
}
vc_choices=[(k,v[0]) for k,v in vc_checks.items()]
##
## Virtual circuit
##
class VC(models.Model):
    class Meta:
        verbose_name="VC"
        verbose_name_plural="VCs"
        unique_together=[("vc_domain","type","l1","l2")]
    vc_domain=models.ForeignKey(VCDomain,verbose_name="VC Domain")
    type=models.CharField("Type",max_length=1,choices=vc_choices)
    l1=models.IntegerField("Label 1")
    l2=models.IntegerField("Label 2",default=0)
    description=models.CharField("Description",max_length=256)

    def __unicode__(self):
        s=u"%s %s %d"%(self.vc_domain,self.type,self.l1)
        if self.l2:
            s+=u"/%d"%self.l2
        return s
    
    def save(self):
        def in_range(v,r):
            return (v>=r[0]) and (v<=r[1]) 
        description,min_labels,l1range,l2range=vc_checks[self.type]
        if not in_range(self.l1,l1range):
            raise Exception("Invalid value for L1")
        if min_labels>1 and not self.l2:
            raise Exception("L2 required for type %s"%self.type)
        if min_labels>1 and not in_range(self.l2,l2range):
            raise Exception("Invalid value for L2")
        super(VC,self).save()
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
        ])
    ]
