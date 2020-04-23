# ----------------------------------------------------------------------
# vrf vpn_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.vpn import get_vpn_id
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.add_column(
            "ip_vrf", "vpn_id", models.CharField("VPN ID", max_length=15, null=True, blank=True)
        )
        for id, name, rd in self.db.execute("SELECT id, name, rd FROM ip_vrf"):
            vpn_id = get_vpn_id({"type": "VRF", "name": name, "rd": rd})
            self.db.execute("UPDATE ip_vrf SET vpn_id = %s WHERE id = %s", [vpn_id, id])
        self.db.execute("ALTER TABLE ip_vrf ALTER vpn_id SET NOT NULL")
        self.db.execute("ALTER TABLE ip_vrf ADD CONSTRAINT vpn_id_unique UNIQUE (vpn_id)")
