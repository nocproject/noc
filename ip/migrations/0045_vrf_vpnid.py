# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models
from noc.core.vpn import get_vpn_id


class Migration(object):
    def forwards(self):
        db.add_column(
            "ip_vrf",
            "vpn_id",
            models.CharField(
                "VPN ID",
                max_length=15,
                null=True, blank=True
            )
        )
        for id, name, rd in db.execute("SELECT id, name, rd FROM ip_vrf"):
            vpn_id = get_vpn_id({
                "type": "VRF",
                "name": name,
                "rd": rd
            })
            db.execute("UPDATE ip_vrf SET vpn_id = %s WHERE id = %s", [
                vpn_id,
                id
            ])
        db.execute("ALTER TABLE ip_vrf ALTER vpn_id SET NOT NULL")
        db.execute("ALTER TABLE ip_vrf ADD CONSTRAINT vpn_id_unique UNIQUE (vpn_id)")

    def backwards(self):
        pass
