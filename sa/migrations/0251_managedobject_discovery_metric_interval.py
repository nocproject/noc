# ----------------------------------------------------------------------
# Add effective_metric_discovery_interval field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import IntegerField

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Add effective_metric_discovery_interval columns
        self.db.add_column(
            "sa_managedobject",
            "effective_metric_discovery_interval",
            IntegerField(
                default=0,
                null=True,
                blank=True,
            ),
        )
        self.db.execute(
            """
        UPDATE sa_managedobject as mo
        SET effective_metric_discovery_interval = mop.metrics_default_interval
        FROM sa_managedobjectprofile as mop
        WERE mo.object_profile_id = mop.id
        """
        )
