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


class Lane(nosql.Document):
    meta = {
        "collection": "noc.wf.lanes",
        "allow_inheritance": False
    }

    workflow = nosql.PlainReferenceField(Workflow)
    name = nosql.StringField()
    is_active = nosql.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.workflow, self.name)
