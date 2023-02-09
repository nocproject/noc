# ----------------------------------------------------------------------
# Add inetrval metrics discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson
from django.db.models import IntegerField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        metric_intervals = {}  # object_profile -> metrics_default_interval
        box_collected_metrics = {}  # object_profile -> box_interval
        for (
            mop_id,
            enable_box_metrics,
            box_interval,
            enable_periodic_metrics,
            periodic_interval,
        ) in self.db.execute(
            """SELECT id, enable_box_discovery_metrics, box_discovery_interval, enable_periodic_discovery_metrics, periodic_discovery_interval FROM sa_managedobjectprofile"""
        ):
            if enable_periodic_metrics and periodic_interval != 300:
                metric_intervals[mop_id] = periodic_interval
            if enable_box_metrics:
                box_collected_metrics[mop_id] = box_interval
        # Add metrics_default_interval columns
        self.db.add_column(
            "sa_managedobjectprofile", "metrics_default_interval", IntegerField(default=300)
        )
        self.db.rename_column(
            "sa_managedobjectprofile", "enable_periodic_discovery_metrics", "enable_metrics"
        )
        # Delete
        self.db.delete_column("sa_managedobjectprofile", "enable_box_discovery_metrics")
        # Update default metrics interval
        for mop_id, interval in metric_intervals.items():
            self.db.execute(
                """UPDATE sa_managedobjectprofile SET metrics_default_interval = %s WHERE id=%s""",
                [mop_id, interval],
            )
        if not box_collected_metrics:
            return
        # Proccessed Box metrics
        for mop_id, metrics in self.db.execute(
            """SELECT id, metrics FROM sa_managedobjectprofile WHERE id = ANY (%s)""",
            [list(box_collected_metrics)],
        ):
            for m in metrics:
                if m.get("is_box"):
                    m["interval"] = box_collected_metrics[mop_id]
            self.db.execute(
                """UPDATE sa_managedobjectprofile SET metrics = %s::jsonb WHERE id = %s""",
                [orjson.dumps(metrics).decode("utf-8"), mop_id],
            )
