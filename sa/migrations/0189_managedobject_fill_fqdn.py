# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fill ManagedObject.fqdn field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from noc.lib.validators import is_ipv4, is_ipv6


class Migration(object):
    def forwards(self):
        fixes = []
        for mo_id, address in db.execute("SELECT id, address FROM sa_managedobject"):
            if not address:
                continue
            if is_ipv4(address) or is_ipv6(address):
                continue
            fixes += [str(mo_id)]
        if not fixes:
            return
        db.execute("""
            UPDATE sa_managedobject
            SET fqdn=address, address_resolution_policy='O'
            WHERE id IN (%s)
            """ % ",".join(fixes)
        )

    def backwards(self):
        pass
