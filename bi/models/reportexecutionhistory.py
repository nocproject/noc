# ----------------------------------------------------------------------
# ReportExecutionHistory Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.clickhouse.model import Model
from noc.core.clickhouse.fields import (
    DateField,
    DateTimeField,
    StringField,
    UInt32Field,
    BooleanField,
)
from noc.core.clickhouse.engines import MergeTree


class ReportExecutionHistory(Model):
    class Meta(object):
        db_table = "reportexecutionhistory"
        engine = MergeTree("date", ("date", "report"))

    date = DateField()
    start = DateTimeField(description="Start execution time")
    end = DateTimeField(description="End execution time")
    duration = UInt32Field(description="Execute duration")
    report = StringField(description="Report UUID")
    name = StringField(description="Report Name")
    code = StringField(description="Report Code")
    user = StringField(description="Requesting User")
    output_document = StringField(description="Link to output document")
    successfully = BooleanField(description="Successful execute")
    canceled = BooleanField(description="Report was cancelled")
    params = StringField(description="Report Params")
    error = StringField(description="Execution error")
    process_id = StringField("Process endpoint")
