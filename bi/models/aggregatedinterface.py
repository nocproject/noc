# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AggregateInterface Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re
# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField, DateTimeField, UInt64Field, UInt32Field, StringField,
    ReferenceField, ArrayField, AggregatedField)
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.clickhouse.engines import AggregatingMergeTree
from noc.core.translation import ugettext as _

agg_param = re.compile(r"^(?P<function>\w+)\((?P<f_param>\S+)\)\((?P<field>\S+)\)$")
agg_wo_param = re.compile(r"^(?P<function>\w+)\((?P<field>\S+)\)$")


class AggregatedInterface(Model):
    class Meta:
        db_table = "AggregatedInterface"
        engine = AggregatingMergeTree("date", ("hour", "managed_object", "date"))

    date = DateField(description=_("Date"))
    hour = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(
        ManagedObject,
        description=_("Object Name"),
        model="sa.ManagedObject"
    )
    path = ArrayField(StringField())
    load_in = AggregatedField(UInt64Field, ["avg", "max", "quantile(0.95)"],
                              description="Load In Aggregate",
                              f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    load_out = AggregatedField(UInt64Field, ["avg", "max", "quantile(0.95)"],
                               f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    packets_in = AggregatedField(UInt64Field, ["avg", "max", "quantile(0.95)"],
                                 f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    packets_out = AggregatedField(UInt64Field, ["avg", "max", "quantile(0.95)"],
                                  f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    discards_in = AggregatedField(UInt32Field, ["avg", "max", "quantile(0.95)"],
                                  f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    discards_out = AggregatedField(UInt32Field, ["avg", "max", "quantile(0.95)"],
                                   f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    errors_in = AggregatedField(UInt32Field, ["avg", "max", "quantile(0.95)"],
                                f_expr="{p[function]}Merge({p[field]}_{p[function]})")
    errors_out = AggregatedField(UInt32Field, ["avg", "max", "quantile(0.95)"],
                                 f_expr="{p[function]}Merge({p[field]}_{p[function]})")
