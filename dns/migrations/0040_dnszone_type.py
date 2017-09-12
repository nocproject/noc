# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DNSZone.type field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VC.project
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "dns_dnszone", "type",
            models.CharField(
                _("Type"),
                max_length=1, null=False, blank=False,
                default="F",
                choices=[
                    ("F", "Forward"),
                    ("4", "Reverse IPv4"),
                    ("6", "Reverse IPv6")
                ]
            )
        )
        db.execute("UPDATE dns_dnszone SET type = '4' WHERE name ILIKE '%%.in-addr.arpa'")
        db.execute("UPDATE dns_dnszone SET type = '6' WHERE name ILIKE '%%.ip6.int' OR name ILIKE '.ip6.arpa'")

    def backwards(self):
        db.drop_column("dns_dnszone", "type")
