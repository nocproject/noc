# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject ResourceGroup integration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from noc.core.model.fields import ObjectIDArrayField


class Migration(object):
    def forwards(self):
        db.add_column(
            "sa_managedobject",
            "static_service_groups",
            ObjectIDArrayField(db_index=True, default="{}")
        )
        db.add_column(
            "sa_managedobject",
            "effective_service_groups",
            ObjectIDArrayField(db_index=True, default="{}")
        )
        db.add_column(
            "sa_managedobject",
            "static_client_groups",
            ObjectIDArrayField(db_index=True, default="{}")
        )
        db.add_column(
            "sa_managedobject",
            "effective_client_groups",
            ObjectIDArrayField(db_index=True, default="{}")
        )

    def backwards(self):
        pass
