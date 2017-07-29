# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Span Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField, DateTimeField, UInt64Field, UInt32Field, StringField)
from noc.core.clickhouse.engines import MergeTree
from noc.core.translation import ugettext as _


class Span(Model):
    class Meta:
        db_table = "span"
        engine = MergeTree("date", ("server", "service", "ts", "in_label"))

    date = DateField(description=_("Date"))
    ts = DateTimeField(description=_("Created"))
    ctx = UInt64Field(description=_("Span context"))
    id = UInt64Field(description=_("Span id"))
    parent = UInt64Field(description=_("Span parent"))
    server = StringField(description=_("Called service"))
    service = StringField(description=_("Called function"))
    client = StringField(description=_("Caller service"))
    duration = UInt64Field(description=_("Duration (us)"))
    sample = UInt32Field(description=_("Sampling rate"))
    error_code = UInt32Field(description=_("Error code"))
    error_text = StringField(description=_("Error text"))
    in_label = StringField(description=_("Input arguments"))
    out_label = StringField(description=_("Output results"))
