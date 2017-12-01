# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Initialize cleanup_metric_is_active field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sla.models.slaprofile import SLAProfile


class Migration:
    def forwards(self):
        collections = [
            InterfaceProfile._get_collection(),
            SLAProfile._get_collection()
        ]
        for collection in collections:
            bulk = []
            for ip in collection.find({
                "metrics.is_active": {
                    "$exists": True
                }
            }):
                metrics = []
                if "metrics" not in ip:
                    continue  # Not configured
                for metric in ip["metrics"]:
                    metric["enable_periodic"] = bool(metric.get("is_active", False))
                    metric["enable_box"] = False
                    if "is_active" in metric:
                        del metric["is_active"]
                    metrics += [metric]
                bulk += [UpdateOne({
                    "_id": ip["_id"]
                }, {
                    "$set": {
                        "metrics": metrics
                    }
                })]
            if bulk:
                collection.bulk_write(bulk)

        for mop in ManagedObjectProfile.objects.filter():
            if not mop.metrics:
                continue
            metrics = []
            for metric in mop.metrics:
                if not metric:
                    continue
                metric["enable_periodic"] = bool(metric.get("is_active", False))
                metric["enable_box"] = False
                if "is_active" in metric:
                    del metric["is_active"]
                metrics += [metric]
            mop.metrics = metrics
            mop.save()

    def backwards(self):
        pass
