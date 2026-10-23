# ----------------------------------------------------------------------
# save user access
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        i = 0
        for user_id, administrative_domain_id, group_id in self.db.execute(
            "SELECT user_id,administrative_domain_id,group_id FROM sa_useraccess"
        ):
            name = f"NOC_UA_{int(user_id)}_{int(i)}"
            self.db.execute(
                """
                INSERT INTO sa_managedobjectselector(name,description,filter_administrative_domain_id)
                VALUES(%s,%s,%s)""",
                [
                    name,
                    f"Auto created from ({user_id},{administrative_domain_id},{group_id})",
                    administrative_domain_id,
                ],
            )
            if group_id:
                s_id = self.db.execute(
                    "SELECT id FROM sa_managedobjectselector WHERE name=%s", [name]
                )[0][0]
                self.db.execute(
                    """
                    INSERT INTO sa_managedobjectselector_filter_groups(managedobjectselector_id,objectgroup_id)
                    VALUES(%s,%s)""",
                    [s_id, group_id],
                )
            i += 1
