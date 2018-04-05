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
    def forwards(self):
        db.add_column(
            "sa_managedobjectprofile",
            "prefix_profile_interface",
            DocumentReferenceField(
                "ip.PrefixProfile",
                null=True, blank=True
            )
        )
        db.add_column(
            "sa_managedobjectprofile",
            "prefix_profile_neighbor",
            DocumentReferenceField(
                "ip.PrefixProfile",
                null=True, blank=True
            )
        )

    def backwards(self):
        pass
