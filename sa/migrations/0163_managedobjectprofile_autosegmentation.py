# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Add ManagedObjectProfile.mac_collect_* fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from django.db import models


class Migration:
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "autosegmentation_policy",
            models.CharField(
                max_length=1,
                choices=[
                    # Do not allow to move object by autosegmentation
                    ("d", "Do not segmentate"),
                    # Allow moving of object to another segment
                    # by autosegmentation process
                    ("e", "Allow autosegmentation"),
                    # Create additional segment, related to this object,
                    # and move all satisfying objects to it
                    ("o", "Segmentate for object"),
                    # Create additional segment for each interface
                    # and move all satisfying objects to it
                    ("i", "Segmentate for interface")
                ],
                default="d"
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "autosegmentation_level_limit",
            models.IntegerField("Level", default=999)
        )
        db.add_column(
            "sa_managedobjectprofile",
            "autosegmentation_segment_name",
            models.CharField(
                max_length=255,
                default="{{object.name}}{% if object.profile.autosegmentation_policy == 'i' %}-{{interface.name}}{% endif %}"
            ))

    def backwards(self):
        db.delete_column("sa_managedobjectprofile",
                         "autosegmentation_policy")
        db.delete_column("sa_managedobjectprofile",
                         "autosegmentation_level_limit")
        db.delete_column("sa_managedobjectprofile",
                         "autosegmentation_segment_name")
