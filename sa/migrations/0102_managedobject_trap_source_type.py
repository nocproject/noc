# ----------------------------------------------------------------------
# managedobject trap_source_type
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0055_default_pool")]

    def migrate(self):
        self.db.add_column(
            "sa_managedobject",
            "trap_source_type",
            models.CharField(
                max_length=1,
                choices=[
                    ("d", "Disable"),
                    ("m", "Management Address"),
                    ("s", "Specify address"),
                    ("l", "Loopback address"),
                    ("a", "All interface addresses"),
                ],
                default="d",
                null=False,
                blank=False,
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "syslog_source_type",
            models.CharField(
                max_length=1,
                choices=[
                    ("d", "Disable"),
                    ("m", "Management Address"),
                    ("s", "Specify address"),
                    ("l", "Loopback address"),
                    ("a", "All interface addresses"),
                ],
                default="d",
                null=False,
                blank=False,
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "syslog_source_ip",
            models.GenericIPAddressField("Syslog Source IP", null=True, protocol="IPv4"),
        )
        self.db.execute(
            """UPDATE sa_managedobject
                SET trap_source_type='s', syslog_source_ip=trap_source_ip, syslog_source_type='s'
                WHERE trap_source_ip IS NOT NULL"""
        )
