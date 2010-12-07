# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map/Reduce task  Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
import datetime
## NOC modules
from noc.lib.app.simplereport import *
from noc.sa.models import ReduceTask
##
## Map/Reduce task report
##
class ReportMRTask(SimpleReport):
    title="Active Map/Reduce tasks"
    def get_data(self,**kwargs):
        r=[]
        now=datetime.datetime.now()
        for rt in ReduceTask.objects.all().order_by("-stop_time"):
            r+=[SectionRow("#%d. %s"%(rt.id,"[Complete]" if rt.stop_time else "[Running]"))]
            for mt in rt.maptask_set.all():
                r+=[(mt.managed_object.name, mt.map_script, mt.status, mt.script_result)]
        return self.from_dataset(title=self.title,
            columns=["Object","Script","Status", TableColumn("Result", format="pprint")],data=r)
    
