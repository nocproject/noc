# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map/Reduce task  Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Python modules
import datetime
# Django modules
from django.utils.dateformat import DateFormat
## NOC modules
from noc.lib.app.simplereport import *
from noc.sa.models import ReduceTask
from noc import settings
##
## Map/Reduce task report
##
class ReportMRTask(SimpleReport):
    title="Active Map/Reduce tasks"
    def get_data(self,**kwargs):
        dt=lambda f: DateFormat(f).format(settings.DATETIME_FORMAT)
        r=[]
        now=datetime.datetime.now()
        for rt in ReduceTask.objects.all().order_by("-stop_time"):
            r+=[SectionRow("#%d. %s. %s - %s"%(rt.id, "[Complete]" if rt.stop_time else "[Running]", dt(rt.start_time), dt(rt.stop_time)))]
            for mt in rt.maptask_set.all().only("managed_object__name", "map_script", "status"):
                r+=[(mt.managed_object.name, mt.map_script, mt.get_status_display())]
        return self.from_dataset(title=self.title,
            columns=["Object","Script","Status"], data=r)
    
