# ----------------------------------------------------------------------
# move type
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
        VCType = self.db.mock_model(model_name="VCType", db_table="vc_vctype")
        self.db.add_column(
            "vc_vcdomain",
            "type",
            models.ForeignKey(
                VCType, verbose_name="type", blank=True, null=True, on_delete=models.CASCADE
            ),
        )
        # VLAN Type
        (vlan_type,) = self.db.execute("SELECT id FROM vc_vctype WHERE name=%s", ["802.1Q VLAN"])[0]
        # Fill vc_domain.type_id
        for vc_domain_id, domain_name in self.db.execute("SELECT id,name FROM vc_vcdomain"):
            (count,) = self.db.execute(
                "SELECT COUNT(DISTINCT type_id) FROM vc_vc WHERE vc_domain_id=%s", [vc_domain_id]
            )[0]
            if count == 0:  # Set default type for empty domains
                self.db.execute(
                    "UPDATE vc_vcdomain SET type_id=%s WHERE id=%s", [vlan_type, vc_domain_id]
                )
            elif count == 1:
                (type_id,) = self.db.execute(
                    "SELECT DISTINCT type_id FROM vc_vc WHERE vc_domain_id=%s", [vc_domain_id]
                )[0]
                self.db.execute(
                    "UPDATE vc_vcdomain SET type_id=%s WHERE id=%s", [type_id, vc_domain_id]
                )
            else:  # Crazy combination
                types = self.db.execute(
                    "SELECT DISTINCT type_id FROM vc_vc WHERE vc_domain_id=%s", [vc_domain_id]
                )
                t0 = types.pop(0)[0]
                self.db.execute("UPDATE vc_vcdomain SET type_id=%s WHERE id=%s", [t0, vc_domain_id])
                i = 0
                for (t,) in types:
                    # Create stub
                    n = domain_name + " %d" % i
                    self.db.execute(
                        "INSERT INTO vc_vcdomain(name,type_id,description) VALUES(%s,%s,%s)",
                        [n, t, "Collision Resolved"],
                    )
                    (d_id,) = self.db.execute("SELECT id FROM vc_vcdomain WHERE name=%s", [n])[0]
                    # Fix collisions
                    self.db.execute(
                        "UPDATE vc_vc SET vc_domain_id=%s WHERE vc_domain_id=%s AND type_id=%s",
                        [d_id, vc_domain_id, t],
                    )
