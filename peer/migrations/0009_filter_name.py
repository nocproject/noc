# ----------------------------------------------------------------------
# filter name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "peer_peer",
            "import_filter_name",
            models.CharField("Import Filter Name", max_length=64, blank=True, null=True),
        )
        self.db.add_column(
            "peer_peer",
            "export_filter_name",
            models.CharField("Export Filter Name", max_length=64, blank=True, null=True),
        )
        self.db.add_column(
            "peer_peeringpoint",
            "provision_rcmd",
            models.CharField("Provisioning URL", max_length=128, blank=True, null=True),
        )
