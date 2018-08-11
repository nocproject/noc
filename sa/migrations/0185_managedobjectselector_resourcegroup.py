# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectSelector.filter_service_group and .filter_client_group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobjectselector",
            "filter_service_group",
            DocumentReferenceField("inv.ResourceGroup", null=True, blank=True)
        )
        db.add_column(
            "sa_managedobjectselector",
            "filter_client_group",
            DocumentReferenceField("inv.ResourceGroup", null=True, blank=True)
        )

    def backwards(self):
        pass
