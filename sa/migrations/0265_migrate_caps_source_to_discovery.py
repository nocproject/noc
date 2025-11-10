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
            SET caps = (select jsonb_agg(CASE
            WHEN element @> '{"source": "caps"}' THEN element||'{"source": "discovery"}'
            WHEN element @> '{"source": "attributes"}' THEN element||'{"source": "database"}'
            WHEN element @> '{"source": "interface"}' THEN element||'{"source": "database"}'
            WHEN element @> '{"source": "sla"}' THEN element||'{"source": "database"}'
            WHEN element @> '{"source": "cpe"}' THEN element||'{"source": "database"}'
            WHEN element @> '{"source": "asset"}' THEN element||'{"source": "database"}'
            WHEN element @> '{"source": "bgppeer"}' THEN element||'{"source": "database"}'
            ELSE element END)
            FROM jsonb_array_elements(caps) as x(element))
            WHERE caps @> '[{"source": "caps"}]' OR caps @> '[{"source": "interface"}]'
                  OR caps @> '[{"source": "asset"}]' OR caps @> '[{"source": "attributes"}]'
                  OR caps @> '[{"source": "bgppeer"}]'
        """
        )
