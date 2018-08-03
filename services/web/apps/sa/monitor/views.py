# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.monitor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python module
import re
import zlib
#  # NOC modules
from noc.lib.nosql import get_db
from noc.services.web.apps.sa.objectlist.views import ObjectListApplication
from noc.lib.dateutils import humanize_distance
from noc.core.scheduler.scheduler import Scheduler
from noc.core.scheduler.job import Job
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _
from noc.lib.app.modelapplication import ModelApplication


class TaskMonitorApplication(ObjectListApplication):
    """
    sa.monitor application
    """
    title = _("Monitor")
    menu = _("Monitor")
    icon = "icon_monitor"

    def get_job_data(self, scheduler, pool=None, status=None, key=None, jcls=None):
        result = []
        scheduler = Scheduler(
            name=scheduler,
            pool=pool,
        )
        if status:
            q = {"s": status}
        if key:
            q = {"jcls": jcls, "key": key}
        for r in scheduler.get_collection().find(q):
            res = r["key"]
            result.append(res)
        return result

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """

        status = request.POST.get("status")
        if not status:
            status = "R"
        self.logger.info("Queryset %s" % query)
        res = []
        for p in Pool.objects.filter():
            if p.name == "P0001":
                continue
            r = self.get_job_data("discovery", pool=p.name, status=status)
            res += r
        return self.model.objects.filter(id__in=res)

    def instance_to_dict(self, mo, fields=None):

        rx_time = re.compile(r"Completed. Status: SUCCESS\s\((?P<time>\S+)\)", re.MULTILINE)
        b_last_success = '--'
        b_last_status = None
        b_time_start = None
        b_status = None
        b_time = '--'
        p_last_success = '--'
        p_last_status = None
        p_time_start = None
        p_status = None
        p_time = '--'

        box_jcls = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        periodic_jcls = "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"

        box_job = Job.get_job_data("discovery",
                                   jcls=box_jcls,
                                   key=mo.id,
                                   pool=mo.pool.name
                                   )

        periodic_job = Job.get_job_data("discovery",
                                        jcls=periodic_jcls,
                                        key=mo.id,
                                        pool=mo.pool.name
                                        )
        if box_job:
            b_last_success = humanize_distance(box_job["last"]) if "last" in box_job else '--'
            b_last_status = box_job.get(Job.ATTR_LAST_STATUS)
            b_time_start = self.to_json(box_job.get(Job.ATTR_TS))
            b_status = box_job["s"] if "s" in box_job else '--'
            if b_status == "W":
                bkey = "discovery-%s-%s" % (box_jcls, mo.id)
                bd = get_db()["noc.joblog"].find_one({"_id": bkey})
                if bd and bd["log"]:
                    br = ModelApplication.render_plain_text(zlib.decompress(str(bd["log"])))
                    match = rx_time.search(str(br))
                    if match:
                        s = match.group("time").split(".")[0]
                        if len(s) > 3:
                            b_time = "%s sec" % (int(s) / 1000)
                        else:
                            b_time = "%s mc" % s
        if periodic_job:
            # print periodic_job
            p_last_success = humanize_distance(periodic_job["last"]) if "last" in periodic_job else '--'
            p_last_status = periodic_job.get(Job.ATTR_LAST_STATUS)
            p_time_start = self.to_json(periodic_job.get(Job.ATTR_TS))
            # print p_time_start
            p_status = periodic_job["s"] if "s" in periodic_job else '--'
            if p_status == "W":
                pkey = "discovery-%s-%s" % (periodic_jcls, mo.id)
                pd = get_db()["noc.joblog"].find_one({"_id": pkey})
                if pd and pd["log"]:
                    pr = ModelApplication.render_plain_text(zlib.decompress(str(pd["log"])))
                    match = rx_time.search(str(pr))
                    if match:
                        s = match.group("time").split(".")[0]
                        if len(s) > 3:
                            p_time = "%s sec" % (int(s) / 1000)
                        else:
                            p_time = "%s mc" % s
        return {
            'id': str(mo.id),
            'name': mo.name,
            'address': mo.address,
            'profile_name': mo.profile.name,
            'platform': mo.platform.name if mo.platform else "",
            'b_time_start': b_time_start,
            'b_last_success': b_last_success,
            'b_status': b_status,
            "b_time": b_time,
            'b_duration': "",
            'b_last_status': b_last_status,
            'p_time_start': p_time_start,
            'p_last_success': p_last_success,
            'p_status': p_status,
            'p_duration': "",
            'p_last_status': p_last_status,
            "p_time": p_time
        }
