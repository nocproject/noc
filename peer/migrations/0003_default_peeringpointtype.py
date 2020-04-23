# ----------------------------------------------------------------------
# default peeringpointtype
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

LEGACY = [
    ("Cisco", "Cisco.IOS"),
    ("Juniper", "Juniper.JUNOS"),
    ("IOS", "Cisco.IOS"),
    ("JUNOS", "Juniper.JUNOS"),
]
TYPES = ["Cisco.IOS", "Juniper.JUNOS"]


class Migration(BaseMigration):
    def migrate(self):
        for f, t in LEGACY:
            self.db.execute("UPDATE peer_peeringpointtype SET name=%s WHERE name=%s", [t, f])
        for t in TYPES:
            if (
                self.db.execute("SELECT COUNT(*) FROM peer_peeringpointtype WHERE name=%s", [t])[0][
                    0
                ]
                == 0
            ):
                self.db.execute("INSERT INTO peer_peeringpointtype(name) VALUES(%s)", [t])
