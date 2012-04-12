# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VRF.state
## Prefix.state
## IP.state
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from south.db import db
## NOC modules
from noc.ip.models import *


class Migration:
    depends_on = (
        ("main", "0043_default_resourcestates"),
    )

    def forwards(self):
        # Create .state
        ResourceState = db.mock_model(model_name="ResourceState",
            db_table="main_resourcestate", db_tablespace="", pk_field_name="id",
            pk_field_type=models.AutoField)
        db.add_column("ip_vrf", "state",
            models.ForeignKey(ResourceState, verbose_name="State",
                null=True, blank=True))
        db.add_column("ip_prefix", "state",
            models.ForeignKey(ResourceState, verbose_name="State",
                null=True, blank=True))
        db.add_column("ip_address", "state",
            models.ForeignKey(ResourceState, verbose_name="State",
                null=True, blank=True))

    def backwards(self):
        db.drop_column("ip_vrf", "state_id")
        db.drop_column("ip_prefix", "state_id")
        db.drop_column("ip_address", "state_id")
