# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Variable model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql
from workflow import Workflow


class Variable(nosql.Document):
    meta = {
        "collection": "noc.wf.variables",
        "allow_inheritance": False
    }

    workflow = nosql.PlainReferenceField(Workflow)
    name = nosql.StringField()
    type = nosql.StringField(
        choices=[
            ("str", "String"),
            ("int", "Integer"),
            ("bool", "Boolean"),
            ("float", "Float")
        ])
    default = nosql.StringField()
    # Required to start the process
    required = nosql.BooleanField()

    def __unicode__(self):
        return "%s %s (%s)" % (self.workflow, self.name, self.type)

    def clean(self, value):
        return getattr(self, "clean_%s" % self.type)(value)

    def clean_str(self, value):
        return value

    def clean_int(self, value):
        return int(value)

    def clean_bool(self, value):
        return value.lower() in ["on", "true", "yes"]

    def clean_float(self, value):
        return float(value)
