# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Classification Rules Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,SectionRow
from noc.fm.models import EventClassificationRule
##
##
##
class Reportreportclassificationrule(SimpleReport):
    title="Classification Rules"
    def get_data(self,**kwargs):
        data=[]
        for r in EventClassificationRule.objects.order_by("preference"):
            data+=[SectionRow("%s (%s)"%(r.name,r.preference))]
            data+=[["Event Class",r.event_class]]
            data+=[["Action",r.action]]
            for rr in r.eventclassificationre_set.all():
                data+=[[rr.left_re,(" = " if rr.is_expression else "")+rr.right_re]]
        return self.from_dataset(title=self.title,columns=["Left RE","Right RE"],data=data)
