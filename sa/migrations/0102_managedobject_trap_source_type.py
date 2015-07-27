# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    depends_on = [
        ("main", "0055_default_pool")
    ]

    def forwards(self):
        db.add_column("sa_managedobject", "trap_source_type",
            models.CharField(
                max_length=1,
                choices=[
                    ("d", "Disable"),
                    ("m", "Management Address"),
                    ("s", "Specify address"),
                    ("l", "Loopback address"),
                    ("a", "All interface addresses")
                ],
                default="d", null=False, blank=False
            )
        )
        db.add_column("sa_managedobject", "syslog_source_type",
            models.CharField(
                max_length=1,
                choices=[
                    ("d", "Disable"),
                    ("m", "Management Address"),
                    ("s", "Specify address"),
                    ("l", "Loopback address"),
                    ("a", "All interface addresses")
                ],
                default="d", null=False, blank=False
            )
        )
        db.add_column(
            "sa_managedobject", "syslog_source_ip",
            models.IPAddressField("Syslog Source IP", null=True)
        )
        db.execute(
            "UPDATE sa_managedobject "
            "SET trap_source_type='s', "
            "    syslog_source_ip=trap_source_ip, "
            "    syslog_source_type='s' "
            "WHERE trap_source_ip IS NOT NULL"
        )

    def backwards(self):
        pass
