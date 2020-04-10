# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# new vcdomainprovisioningconfig
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("main", "0013_notifications")]

    def migrate(self):
        # Get data
        pc = {}
        for vc_domain_id, selector_id, key, value in self.db.execute(
            "SELECT vc_domain_id,selector_id,key,value FROM vc_vcdomainprovisioningconfig"
        ):
            if vc_domain_id not in pc:
                pc[vc_domain_id] = {}
            if selector_id not in pc[vc_domain_id]:
                pc[vc_domain_id][selector_id] = {"enable": True, "tagged_ports": None}
            pc[vc_domain_id][selector_id][key] = value
            # Alter
        self.db.add_column(
            "vc_vcdomainprovisioningconfig",
            "is_enabled",
            models.BooleanField("Is Enabled", default=True),
        )
        self.db.add_column(
            "vc_vcdomainprovisioningconfig",
            "tagged_ports",
            models.CharField("Tagged Ports", max_length=256, null=True, blank=True),
        )
        NotificationGroup = self.db.mock_model(
            model_name="NotificationGroup", db_table="main_notificationgroup"
        )
        self.db.add_column(
            "vc_vcdomainprovisioningconfig",
            "notification_group",
            models.ForeignKey(
                NotificationGroup,
                verbose_name="Notification Group",
                null=True,
                blank=True,
                on_delete=models.CASCADE,
            ),
        )
        self.db.delete_column("vc_vcdomainprovisioningconfig", "key")
        self.db.delete_column("vc_vcdomainprovisioningconfig", "value")
        # Save data
        self.db.execute("DELETE FROM vc_vcdomainprovisioningconfig")
        for vc_domain_id, c in pc.items():
            for selector_id, v in c.items():
                self.db.execute(
                    """
                    INSERT INTO vc_vcdomainprovisioningconfig
                    (vc_domain_id,selector_id,is_enabled,tagged_ports,notification_group_id) VALUES(%s,%s,%s,%s,%s)""",
                    [
                        vc_domain_id,
                        selector_id,
                        v["enable"].lower() in ["true", "t"],
                        v["tagged_ports"],
                        None,
                    ],
                )
        self.db.execute("COMMIT")
