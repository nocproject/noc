# ----------------------------------------------------------------------
# root object
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if (
            self.db.execute("SELECT COUNT(*) FROM sa_managedobject WHERE name=%s", ["ROOT"])[0][0]
            == 0
        ):
            administrative_domain_id = self.db.execute(
                "SELECT id FROM sa_administrativedomain ORDER BY id"
            )[0][0]
            activator_id = self.db.execute("SELECT id FROM sa_activator ORDER BY id")[0][0]
            self.db.execute(
                """
                INSERT INTO sa_managedobject(name,is_managed,administrative_domain_id,activator_id,profile_name,scheme,
                address,is_configuration_managed) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                ["ROOT", True, administrative_domain_id, activator_id, "NOC", 1, "0.0.0.0", False],
            )
