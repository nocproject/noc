# ----------------------------------------------------------------------
# Auth Profile dynamic classification policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Update sa_authprofile
        self.db.add_column(
            "sa_authprofile",
            "snmp_security_level",
            models.CharField(
                "SNMP protocol security",
                max_length=12,
                choices=[
                    ("Community", "Community"),
                    ("noAuthNoPriv", "noAuthNoPriv"),
                    ("authNoPriv", "authNoPriv"),
                    ("authPriv", "authPriv"),
                ],
                default="Community",
            ),
        )
        self.db.add_column(
            "sa_authprofile",
            "snmp_username",
            models.CharField("SNMP user name", max_length=32, null=True, blank=True),
        )
        self.db.add_column(
            "sa_authprofile",
            "snmp_auth_proto",
            models.CharField(
                "Authentication protocol",
                max_length=3,
                choices=[("MD5", "MD5"), ("SHA", "SHA")],
                default="MD5",
            ),
        )
        self.db.add_column(
            "sa_authprofile",
            "snmp_auth_key",
            models.CharField("Authentication key", max_length=32, null=True, blank=True),
        )
        self.db.add_column(
            "sa_authprofile",
            "snmp_priv_proto",
            models.CharField(
                "Privacy protocol",
                max_length=3,
                choices=[("DES", "DES"), ("AES", "AES")],
                default="DES",
            ),
        )
        self.db.add_column(
            "sa_authprofile",
            "snmp_priv_key",
            models.CharField("Privacy key", max_length=32, null=True, blank=True),
        )
        self.db.add_column(
            "sa_authprofile",
            "snmp_ctx_name",
            models.CharField("Context name", max_length=32, null=True, blank=True),
        )

        # Update managedobjects
        self.db.add_column(
            "sa_managedobject",
            "snmp_security_level",
            models.CharField(
                "SNMP protocol security",
                max_length=12,
                choices=[
                    ("Community", "Community"),
                    ("noAuthNoPriv", "noAuthNoPriv"),
                    ("authNoPriv", "authNoPriv"),
                    ("authPriv", "authPriv"),
                ],
                default="Community",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_username",
            models.CharField("SNMP user name", max_length=32, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_auth_proto",
            models.CharField(
                "Authentication protocol",
                max_length=3,
                choices=[("MD5", "MD5"), ("SHA", "SHA")],
                default="MD5",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_auth_key",
            models.CharField("Authentication key", max_length=32, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_priv_proto",
            models.CharField(
                "Privacy protocol",
                max_length=3,
                choices=[("DES", "DES"), ("AES", "AES")],
                default="DES",
            ),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_priv_key",
            models.CharField("Privacy key", max_length=32, null=True, blank=True),
        )
        self.db.add_column(
            "sa_managedobject",
            "snmp_ctx_name",
            models.CharField("Context name", max_length=32, null=True, blank=True),
        )
