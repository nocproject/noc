# ----------------------------------------------------------------------
# Fill ManagedObject.fqdn field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.validators import is_ipv4, is_ipv6


class Migration(BaseMigration):
    def migrate(self) -> None:
        fixes, dot_fixes = [], []
        for mo_id, address in self.db.execute("SELECT id, address FROM sa_managedobject"):
            if not address:
                continue
            if is_ipv4(address) or is_ipv6(address):
                continue
            if address.endswith("."):
                fixes.append(str(mo_id))
            else:
                dot_fixes.append(str(mo_id))
        if fixes:
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET fqdn=address, address_resolution_policy='O'
                WHERE id IN ({})
                """.format(",".join(fixes))
            )
        if dot_fixes:
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET fqdn=concat(address, '.'), address_resolution_policy='O'
                WHERE id IN ({})
                """.format(",".join(dot_fixes))
            )
