# ----------------------------------------------------------------------
# vc provisioning
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("sa", "0015_managedobjectselector")]

    def migrate(self):
        VCDomain = self.db.mock_model(model_name="VCDomain", db_table="vc_vcdomain")
        ManagedObjectSelector = self.db.mock_model(
            model_name="ManagedObjectSelector", db_table="sa_managedobjectselector"
        )

        # Adding model 'VCDomainProvisioningConfig'
        self.db.create_table(
            "vc_vcdomainprovisioningconfig",
            (
                ("id", models.AutoField(primary_key=True)),
                (
                    "vc_domain",
                    models.ForeignKey(VCDomain, verbose_name="VC Domain", on_delete=models.CASCADE),
                ),
                (
                    "selector",
                    models.ForeignKey(
                        ManagedObjectSelector,
                        verbose_name="Managed Object Selector",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("key", models.CharField("Key", max_length=64)),
                ("value", models.CharField("Value", max_length=256)),
            ),
        )

        # Creating unique_together for [vc_domain, selector, key] on VCDomainProvisioningConfig.
        self.db.create_index(
            "vc_vcdomainprovisioningconfig", ["vc_domain_id", "selector_id", "key"], unique=True
        )

        self.db.add_column(
            "vc_vcdomain",
            "enable_provisioning",
            models.BooleanField("Enable Provisioning", default=False),
        )
