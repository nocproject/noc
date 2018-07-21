# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db import models
from south.db import db
# NOC models
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    depends_on = [
        ("ip", "0038_address_name"),
        ("main", "0037_template")
    ]

    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_management",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_address_dhcp",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "address_profile_interface",
            DocumentReferenceField(
                "ip.AddressProfile",
                null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "address_profile_management",
            DocumentReferenceField(
                "ip.AddressProfile",
                null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "address_profile_neighbor",
            DocumentReferenceField(
                "ip.AddressProfile",
                null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "address_profile_dhcp",
            DocumentReferenceField(
                "ip.AddressProfile",
                null=True, blank=True
            )
        )

    def backwards(self):
        pass
