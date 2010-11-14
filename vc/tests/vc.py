# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.vc.models import *

class VCTestCase(ModelTestCase):
    model=VC
    ##
    ## Sample data
    ##
    def get_data(self):
        return [
            {
                "vc_domain_id" : 1,
                "name"         : "VLAN1",
                "l1"           : 1
            },
            {
                "vc_domain_id" : 1,
                "name"         : "VLAN2",
                "l1"           : 2
            },
            {
                "vc_domain_id" : 1,
                "name"         : "VLAN3",
                "l1"           : 3
            },
            {
                "vc_domain_id" : 1,
                "l1"           : 4
            },            
        ]
    ##
    ## Test VC Object properties
    ##
    def object_test(self,o):
        pass
    ##
    ## Test search
    ##
    def test_search(self):
        pass
    ##
    ## Test VC Type restrictions
    ##
    def test_VCType(self):
        # Test each VC Type
        for vct in VCType.objects.all():
            # Create domain
            d=VCDomain(name=vct.name,type=vct)
            d.save()
            # Set L2
            l2=0
            if vct.min_labels>1:
                l2=vct.label2_min if vct.label2_min else vct.label2_max
            # Test label 1
            # Lower range
            vc1=VC(vc_domain=d,name="VC1",l1=vct.label1_min-1 if vct.label1_min>1 else -1,l2=l2)
            try:
                vc1.save()
                assert False
            except InvalidLabelException:
                pass
            # Upper range
            vc2=VC(vc_domain=d,name="VC2",l1=vct.label1_max+1,l2=l2)
            try:
                vc2.save()
                assert False
            except InvalidLabelException:
                pass
            # Normal
            vc3=VC(vc_domain=d,name="VC3",l1=vct.label1_min,l2=l2)
            vc3.save()
            unicode(vc3)
            vc3.delete()
            # Test L2
            if vct.min_labels>1:
                l1=vct.label1_min
                vc4=VC(vc_domain=d,name="VC4",l1=l1,l2=vct.label2_min-1 if vct.label2_min>1 else -1)
                try:
                    vc4.save()
                    assert False
                except InvalidLabelException:
                    pass
                vc5=VC(vc_domain=d,name="VC4",l1=l1,l2=vct.label2_max+1)
                try:
                    vc5.save()
                    assert False
                except InvalidLabelException:
                    pass
                vc6=VC(vc_domain=d,name="VC4",l1=l1,l2=vct.label2_min if vct.label2_min else vct.label2_max)
                vc6.save()
                unicode(vc6)
                vc6.prefix_set.all()
                vc6.delete()
            # Clean up domain
            d.delete()
