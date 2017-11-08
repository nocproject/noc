# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Initialize tags
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.nosql import get_db
# Third-party modules
from south.db import db


class Migration:
    depends_on = (
        ("dns", "0034_finish_tag_migration"),
        ("ip", "0024_finish_tag_migration"),
        ("peer", "0037_finish_tag_migration"),
        ("sa", "0063_finish_tag_migration"),
        ("vc", "0022_finish_tag_migration")
    )

    def forwards(self):
        c = get_db().noc.tags
        for m in [
            "sa_activator", "sa_managedobject", "sa_commandsnippet",
            "ip_vrfgroup", "ip_vrf", "ip_prefix", "ip_address",
            "ip_addressrange", "dns_dnszone", "dns_dnszonerecord",
            "vc_vc", "peer_as", "peer_asset", "peer_peer"]:
            for tag, count in db.execute("""
                SELECT unnest(tags), COUNT(*)
                FROM %s
                GROUP BY 1
                """ % m):
                c.update(
                    {"tag": tag},
                    {
                        "$addToSet": {
                            "models": m
                        },
                        "$inc": {
                            "count": int(count)
                        }
                    },
                    upsert=True
                )

    def backwards(self):
        pass
