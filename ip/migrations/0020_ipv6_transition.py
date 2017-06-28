# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PrefixTransition and AddressTransition
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.db import models
# Third-party modules
from south.db import db


class Migration:
    def forwards(self):
        Prefix = db.mock_model(model_name="Prefix",
                               db_table="ip_prefix", db_tablespace="",
                               pk_field_name="id",
                               pk_field_type=models.AutoField)

        Address = db.mock_model(model_name="Address",
                                db_table="ip_address", db_tablespace="",
                                pk_field_name="id",
                                pk_field_type=models.AutoField)

        db.add_column("ip_prefix", "ipv6_transition",
                      models.OneToOneField(Prefix, null=True, blank=True))
        db.add_column("ip_address", "ipv6_transition",
                      models.OneToOneField(Address, null=True, blank=True))

    def backwards(self):
        db.drop_column("ip_prefix", "ipv6_transition_id")
        db.drop_column("ip_address", "ipv6_transition_id")
