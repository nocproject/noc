# ----------------------------------------------------------------------
# Initialize cleanup_metric_is_active field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.sa.models.managedobjectprofile import ManagedObjectProfile


class Migration(BaseMigration):
    def migrate(self):
        # Check ManagedObjectProfile in DB
        mop_req = self.db.execute(
            "SELECT count(*) FROM sa_managedobjectprofile where length(metrics) > 6"
        )
        if mop_req[0][0] > 1:
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
