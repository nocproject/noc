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
            "mac_collect_all",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "mac_collect_interface_profile",
            models.BooleanField(default=True)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "mac_collect_management",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "mac_collect_multicast",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "mac_collect_vcfilter",
            models.BooleanField(default=False)
        )

    def backwards(self):
        db.delete_column("sa_managedobjectprofile", "mac_collect_all")
        db.delete_column("sa_managedobjectprofile", "mac_collect_interface_profile")
        db.delete_column("sa_managedobjectprofile", "mac_collect_management")
        db.delete_column("sa_managedobjectprofile", "mac_collect_multicast")
        db.delete_column("sa_managedobjectprofile", "mac_collect_vcfilter")
