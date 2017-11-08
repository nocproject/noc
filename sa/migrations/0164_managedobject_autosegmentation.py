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
            "sa_managedobject",
            "autosegmentation_policy",
            models.CharField(
                max_length=1,
                choices=[
                    # Do not allow to move object by autosegmentation
                    ("p", "Profile"),
                    # Do not allow to move object by autosegmentation
                    ("d", "Do not segmentate"),
                    # Allow moving of object to another segment
                    # by autosegmentation process
                    ("e", "Allow autosegmentation"),
                    # Move seen objects to this object's segment
                    ("o", "Segmentate to existing segment"),
                    # Expand autosegmentation_segment_name template,
                    # ensure that children segment with same name exists
                    # then move seen objects to this segment.
                    # Following context variables are availale:
                    # * object - this object
                    # * interface - interface on which remote_object seen from object
                    # * remote_object - remote object name
                    # To create single segment use templates like {{object.name}}
                    # To create segments on per-interface basic use
                    # names like {{object.name}}-{{interface.name}}
                    ("c", "Segmentate to child segment")
                ],
                default="p"
            )
        )

    def backwards(self):
        db.delete_column("sa_managedobject",
                         "autosegmentation_policy")
