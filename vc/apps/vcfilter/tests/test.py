# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## vcfilter Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelApplicationTestCase
from noc.vc.models import *

class VCFilterTestCase(ModelApplicationTestCase):
    SAMPLE=[1,2,20,50,51,75,100,101,150,200,250]
    FILTERS=[
        ("1"           , [1]),
        ("2-100"       , [2,20,50,51,75,100]),
        ("1,101-200"   , [1,101,150,200]),
        ("1-50,101-200", [1,2,20,50,101,150,200])
    ]
    
    def testFilters(self):
        for expr,result in self.FILTERS:
            f=VCFilter(name=expr,expression=expr)
            f.save()
            unicode(f)
            r=[s for s in self.SAMPLE if f.check(s)]
            self.assertEquals(result,r)
    
    def testSyntax(self):
        # Empty expression
        f1=VCFilter(name="f1",expression="")
        try:
            f1.save()
            assert False
        except SyntaxError:
            pass
        # Invalid syntax
        f2=VCFilter(name="f2",expression="1--2")
        try:
            f2.save()
            assert False
        except SyntaxError:
            pass
        # Invalid label orver
        f3=VCFilter(name="f2",expression="2-1")
        try:
            f3.save()
            assert False
        except SyntaxError:
            pass
