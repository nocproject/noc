# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator job:
## Check link is up
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import AlarmJob


class PerformanceReportJob(AlarmJob):
    name = "check_link"
    map_task = "get_interface_status"

    def get_map_task_params(self):
        return {
            "interface": self.data["interface"]
        }

    def handler(self, object, result):
        """
        Process result like
        <object>, [{'interface': 'Gi 1/0', 'status': True}]
        :param object:
        :param result:
        :return:
        """
        if len(result) == 1:
            r = result[0]
            if (r["status"] and
                r["interface"] == self.data["interface"]):
                self.clear_alarm("Interface '%s' is up" % (
                    self.data["interface"]))
        return True
