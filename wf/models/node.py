# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Node model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql
from workflow import Workflow
from lane import Lane


class Node(nosql.Document):
    meta = {
        "collection": "noc.wf.nodes",
        "allow_inheritance": False
    }

    workflow = nosql.PlainReferenceField(Workflow)
    lane = nosql.PlainReferenceField(Lane)
    name = nosql.StringField()
    description = nosql.StringField()
    handler = nosql.StringField()
    # param -> value
    params = nosql.RawDictField()
    # next node
    next_node = nosql.StringField()
    next_true_node = nosql.StringField()
    next_false_node = nosql.StringField()
    # Graph position
    x = nosql.IntField()
    y = nosql.IntField()

    def __unicode__(self):
        return "%s %s" % (self.workflow, self.name)

    @property
    def handler_class(self):
        m = __import__("noc.wf.handlers", {}, {}, str(self.handler))
        return getattr(m, "%sHandler" % self.handler)
