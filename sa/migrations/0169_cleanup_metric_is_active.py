# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Initialize cleanup_metric_is_active field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


class Migration:
    def forwards(self):

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
