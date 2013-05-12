# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Workflow model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
import noc.lib.nosql as nosql
from solution import Solution
from error import InvalidStartNode


class Workflow(nosql.Document):
    meta = {
        "collection": "noc.wf.workflows",
        "allow_inheritance": False
    }

    # Unique identifier
    name = nosql.StringField()
    # Long name
    display_name = nosql.StringField()
    solution = nosql.PlainReferenceField(Solution)
    version = nosql.IntField()
    is_active = nosql.BooleanField()
    description = nosql.StringField()
    #
    start_node = nosql.StringField()
    # Permissions
    # stat_permission = nosql.StringField()
    # trace_permission = nosql.StringField()
    # kill_permission = nosql.StringField()
    trace = nosql.BooleanField(default=False)

    def __unicode__(self):
        return "%s.%s v%s" % (
            self.solution.name, self.name, self.version)

    def get_node(self, name):
        return Node.objects.filter(workflow=self.id, name=name).first()

    def get_start_node(self):
        return Node.objects.filter(
            workflow=self.id, id=self.start_node).first()

    def run(self, _trace=None, **kwargs):
        """
        Run process
        :param kwargs:
        :return: Process instance
        """
        # Find start node
        start_node = self.get_start_node()
        if not start_node:
            raise InvalidStartNode(self.start_node)
        #
        trace = self.trace if _trace is None else _trace
        # Prepare context
        ctx = {}
        for v in Variable.objects.filter(workflow=self.id):
            if v.name in kwargs:
                ctx[v.name] = v.clean(kwargs[v.name])
            elif v.default:
                ctx[v.name] = v.clean(v.default)
            else:
                ctx[v.name] = None

        p = Process(
            workflow=self,
            context=ctx,
            start_time=datetime.datetime.now(),
            node=start_node,
            trace=trace
        )
        p.save()
        # Schedule job
        p.schedule()
        return p

## Avoid circular references
from variable import Variable
from process import Process
from node import Node