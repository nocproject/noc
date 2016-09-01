# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Reboots model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (DateField, DateTimeField,
                                        StringField, ArrayField,
                                        Float64Field)
from noc.core.clickhouse.engines import MergeTree


class Reboots(Model):
    class Meta:
        db_table = "reboots"
        engine = MergeTree("date", ("ts", "object_id"))

    date = DateField()
    ts = DateTimeField()
    object_id = StringField()
    object_name = StringField()
    ip = StringField()
    profile = StringField()
    object_profile_id = StringField()
    object_profile_name = StringField()
    vendor = StringField()
    platform = StringField()
    version = StringField()
    # Paths
    adm_path = ArrayField(StringField())
    segment_path = ArrayField(StringField())
    container_path = ArrayField(StringField())
    # Coordinates
    x = Float64Field()
    y = Float64Field()
