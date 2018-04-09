# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VPN discovery settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models
# NOC models
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    def forwards(self):
        db.execute("""
          ALTER TABLE sa_managedobjectprofile 
          RENAME enable_box_discovery_vrf 
          TO enable_box_discovery_vpn_interface""")
        db.add_column(
            "sa_managedobjectprofile",
            "enable_box_discovery_vpn_mpls",
            models.BooleanField(default=False)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "vpn_profile_interface",
            DocumentReferenceField(
                "vc.VPNProfile",
                null=True, blank=True
            )

        )
        db.add_column(
            "sa_managedobjectprofile",
            "vpn_profile_mpls",
            DocumentReferenceField(
                "vc.VPNProfile",
                null=True, blank=True
            )
        )

    def backwards(self):
        pass
