# ----------------------------------------------------------------------
# Migrate ManagedObject caps source from 'caps' to 'discovery'
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(
            """
            UPDATE sa_managedobject
            SET caps = (select jsonb_agg(case
            WHEN element @> '{"source": "caps"}' THEN element||'{"source": "discovery"}' ELSE element END)
            FROM jsonb_array_elements(caps) as x(element))
            WHERE caps @> '[{"source": "caps"}]'
        """
        )
