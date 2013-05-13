# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Process model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
import noc.lib.nosql as nosql
from workflow import Workflow
from node import Node
from noc.lib.scheduler.utils import submit_job


class Process(nosql.Document):
    meta = {
        "collection": "noc.wf.processes",
        "allow_inheritance": False
    }

    workflow = nosql.PlainReferenceField(Workflow)
    node = nosql.PlainReferenceField(Node)
    context = nosql.RawDictField()
    start_time = nosql.DateTimeField()
    trace = nosql.BooleanField(default=False)
    sleep_time = nosql.IntField()

    class SleepException(Exception):
        pass

    class CannotSleepError(Exception):
        pass

    def __unicode__(self):
        return "%s at %s (%s)" % (self.workflow, self.node, self.id)

    def info(self, msg):
        logging.info("[%s (PID: %s)] %s" % (
            self.workflow, self.id, msg))

    def update_context_ref(self, node, param, value):
        """
        Update context with variable referenced by node param
        :param node:
        :param param:
        :param value:
        :return:
        """
        self.context[node.params[param]] = value

    def step(self):
        to_sleep = False
        while not to_sleep:
            if self.trace:
                self.info("Entering node '%s' (%s %s) with context %s" % (
                    self.node.name, self.node.handler,
                    self.node.params, self.context
                ))
            handler = self.node.handler_class()
            try:
                r = handler.run(self, self.node)
            except self.SleepException:
                to_sleep = True
            if self.trace:
                self.info("Leaving node '%s' with context %s" % (
                    self.node.name, self.context
                ))
            # Detect next node
            if handler.conditional:
                if r:
                    next_node = self.node.next_true_node
                else:
                    next_node = self.node.next_false_node
            else:
                next_node = self.node.next_node
            # Move to next node
            if next_node:
                if self.trace:
                    self.info("Moving to node '%s'" % next_node.name)
                self.node = next_node
                self.save()
            else:
                if self.trace:
                    self.info("Stopping at node '%s'" % self.node.name)
                return True
        return False  # Suspended

    def schedule(self):
        submit_job("wf.jobs", "wf.wfstep", key=self.id)

    def sleep(self, t):
        if self.node.handler_class().conditional:
            raise self.CannotSleepError(
                "Cannot sleep in conditional handler")
        self.sleep_time = t
        self.save()
        raise self.SleepException
