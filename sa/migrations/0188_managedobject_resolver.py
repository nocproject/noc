# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject resolver settings
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
from django.db import models
# NOC modules
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    def forwards(self):
        # ManagedObject profile
        db.drop_column("sa_managedobjectprofile", "sync_ipam")
        db.drop_column("sa_managedobjectprofile", "fqdn_template")
        db.add_column(
            "sa_managedobjectprofile",
            "fqdn_suffix",
            models.CharField(
                "FQDN suffix",
                max_length=256, null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "address_resolution_policy",
            models.CharField(
                "Address Resolution Policy",
                choices=[
                    ("D", "Disabled"),
                    ("O", "Once"),
                    ("E", "Enabled")
                ],
                max_length=1,
                null=False, blank=False,
                default="D"
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "resolver_handler",
            DocumentReferenceField("main.Handler", null=True, blank=True)
        )
        # Managed Object
        db.add_column(
            "sa_managedobject",
            "fqdn",
            models.CharField(
                "FQDN",
                max_length=256, null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobject",
            "address_resolution_policy",
            models.CharField(
                "Address Resolution Policy",
                choices=[
                    ("P", "Profile"),
                    ("D", "Disabled"),
                    ("O", "Once"),
                    ("E", "Enabled")
                ],
                max_length=1,
                null=False, blank=False,
                default="P"
            )
        )

    def backwards(self):
        pass
