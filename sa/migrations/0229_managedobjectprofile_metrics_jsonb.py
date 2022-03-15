# ----------------------------------------------------------------------
# Migrate ManagedObjectProfile Metrics Field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import orjson
from pickle import loads

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        object_metric_map = {}

        for o_id, metrics in self.db.execute("SELECT id,metrics FROM sa_managedobjectprofile"):
            if not metrics:
                continue
            metrics = loads(metrics)
            if not metrics:
                continue
            object_metric_map[o_id] = orjson.dumps(metrics)
        self.db.delete_column("sa_managedobjectprofile", "metrics")
        self.db.add_column(
            "sa_managedobjectprofile",
            "metrics",
            models.JSONField("Metric Config Items", null=True, blank=True, default=lambda: "[]"),
        )
        for mop_id in object_metric_map:
            self.db.execute(
                """UPDATE sa_managedobjectprofile SET metrics = %s::jsonb WHERE id = %s""",
                [object_metric_map[mop_id].decode("utf-8"), mop_id],
            )
