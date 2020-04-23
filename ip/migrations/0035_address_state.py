# ----------------------------------------------------------------------
# Migrate Address.state field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import DocumentReferenceField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("wf", "0001_default_wf")]

    RSMAP = {
        1: "5a17f78d1bb6270001bd0346",  # Allocated
        2: "5a17f7391bb6270001bd033e",  # Expired
        3: "5a17f7d21bb6270001bd034f",  # Planned
        4: "5a17f6c51bb6270001bd0333",  # Reserved
        5: "5a17f7fc1bb6270001bd0359",  # Suspend
    }
    WF_FREE = "5a17f61b1bb6270001bd0328"

    def migrate(self):
        # Make legacy Address.state_id field nullable
        self.db.execute("ALTER TABLE ip_address ALTER state_id DROP NOT NULL")
        # Create new Address.state
        self.db.add_column(
            "ip_address", "state", DocumentReferenceField("wf.State", null=True, blank=True)
        )
        # Fill Address.state
        for i in range(1, 6):
            self.db.execute(
                """UPDATE ip_address
                SET state = %s
                WHERE state_id = %s
                """,
                [self.RSMAP[i], i],
            )
        self.db.execute(
            """
            UPDATE ip_address
            SET state = %s
            WHERE state_id > 5
            """,
            [self.WF_FREE],
        )
