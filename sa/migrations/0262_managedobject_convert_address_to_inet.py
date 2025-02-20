# ----------------------------------------------------------------------
# managedobject convert address field to Inet type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.validators import is_ipv4, is_ipv6


class Migration(BaseMigration):

    def migrate(self):
        self.db.execute(f"ALTER TABLE sa_managedobject ALTER address DROP NOT NULL")
        # drop index
        self.db.execute("DROP INDEX IF EXISTS x_managedobject_addressprefix")
        # Check Inet value
        bad_address = set()
        try:
            self.db.execute("SELECT address::inet FROM sa_managedobject")
        except Exception:
            # Check on query
            for mo_id, addr in self.db.execute("SELECT id, address FROM sa_managedobject"):
                if not is_ipv4(addr) or not is_ipv6(addr):
                    bad_address.add(mo_id)
        if bad_address:
            self.db.execute(
                "UPDATE sa_managedobject set address = NULL WHERE id = ANY(ARRAY[%s]::INT[])",
                [bad_address],
            )
        # Migrate
        self.db.execute(
            "ALTER TABLE sa_managedobject ALTER COLUMN address TYPE inet USING address::inet"
        )
        # Create index
        self.db.create_index("sa_managedobject", ["address"], unique=False)
