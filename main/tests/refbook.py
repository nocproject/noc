# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for refbooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.main.models import *
##
##
##
class RefBookTestCase(ModelTestCase):
    model=RefBook
    fixtures=["refbook.json"]
    RECORDS=[{"Country":"Russian Federation","Code":"ru"},{"Country":"Ukraine","Code":"ua"}]
    ##
    ## Test all RECORDS in refbook
    ##
    def check_records(self,refbook):
        r=self.RECORDS[:]
        for d in RefBookData.objects.filter(ref_book=refbook):
            v=dict([(f.name,v) for f,v in d.items])
            if v in r:
                r.remove(v)
        self.assertEquals(len(r),0)
    ##
    ## Test RefBook.add_record
    ##
    def test_add_record(self):
        refbook=RefBook.objects.get(name="ISO 3166 Country Codes")
        # Populate refbook
        for f in self.RECORDS:
            refbook.add_record(f)
        # Check refbook populated properly
        self.check_records(refbook)
        # Flush refbook
        refbook.flush_refbook()
    ##
    ## Test RefBook.bulk_upload
    ##
    def test_bulk_upload(self):
        refbook=RefBook.objects.get(name="ISO 3166 Country Codes")
        # Test bulk upload
        refbook.bulk_upload(self.RECORDS)
        # Check refbook populated properly
        self.check_records(refbook)
        # Flush refbook
        refbook.flush_refbook()
        
        