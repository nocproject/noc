# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Span Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re
# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (BaseField,
    DateField, DateTimeField, UInt64Field, Int32Field, UInt32Field, StringField,
    ReferenceField, ArrayField, AggregatedField)
from noc.core.bi.dictionaries.managedobject import ManagedObject
from noc.core.clickhouse.engines import AggregatingMergeTree
from noc.core.translation import ugettext as _

agg_param = re.compile(r"^(?P<function>\w+)\((?P<f_param>\S+)\)\((?P<field>\S+)\)$")
agg_wo_param = re.compile(r"^(?P<function>\w+)\((?P<field>\S+)\)$")


class AggregatedInterface(Model):
    class Meta:
        db_table = "aggregatedinterface"
        engine = AggregatingMergeTree("date", ("hour", "managed_object", "date"))

    date = DateField(description=_("Date"))
    hour = DateTimeField(description=_("Created"))
    managed_object = ReferenceField(
        ManagedObject,
        description=_("Object Name")
    )
    path = ArrayField(StringField)
    # avg AggregateFunction(avg, UInt64),
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

    @classmethod
    def transform_query(cls, query, user):
        # @todo Call parent transform_query
        for field in query["fields"]:
            if "ts" in field["expr"]:
                # No ts field - use hour
                field["expr"] = field["expr"].replace("ts", "hour")
            if "group" in field:
                # Field Group
                continue
            if "(" not in field["expr"]:
                continue
            e = field["expr"]
            match = agg_param.match(e) or agg_wo_param.match(e)
            if not match:
                print("Field format not match")
                continue
            match = match.groupdict()
            attr = match.get("field")
            function = match.get("function")
            f_param = match.get("f_param")
            if not hasattr(cls, attr):
                # not Attribue found
                print("Not found attribute: %s" % attr)
                continue
            attr = getattr(cls, attr)
            if not isinstance(attr, AggregatedField):
                print("Field %s not aggregate, skiping..." % attr.name)
                continue
            field["expr"] = attr.get_expr(function, "")
        print query
        return query
