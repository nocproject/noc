# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Add ManagedObjectProfile.mac_collect_* fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_vrf",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address",
            models.BooleanField(default=True)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_interface",
            models.BooleanField(default=False)
        )
        # db.add_column(
        #     "sa_managedobjectprofile",
        #     "enable_box_discovery_prefix",
        #     models.BooleanField(default=False)
        # )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_prefix_interface",
            models.BooleanField(default=False)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_vrf")
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_address")
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_address_interface")
        # db.delete_column("sa_managedobjectprofile", "enable_box_discovery_prefix")
        db.delete_column("sa_managedobjectprofile", "enable_box_discovery_prefix_interface")
