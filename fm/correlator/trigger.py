# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm trigger
##----------------------------------------------------------------------
## Copyright (C) 2007-2012, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import logging


class Trigger(object):
    def __init__(self, t):
        self.name = t.name
        # Condition
        self.condition = compile(t.condition, "<string>", "eval")
        self.time_pattern = t.time_pattern
        self.selector = t.selector
        # Action
        self.notification_group = t.notification_group
        self.template = t.template
        self.pyrule = t.pyrule

    def match(self, alarm):
        """
        Check event matches trigger condition
        """
        return (eval(self.condition, {}, {"alarm": alarm, "re": re}) and
                (self.time_pattern.match(alarm.timestamp) if self.time_pattern else True) and
                (self.selector.match(alarm.managed_object) if self.selector else True))

    def call(self, alarm):
        if not self.match(alarm):
            return
        logging.debug("Calling trigger '%s'" % self.name)
        # Notify if necessary
        if self.notification_group and self.template:
            self.notification_group.notify(
                subject=self.template.render_subject(alarm=alarm),
                body=self.template.render_body(alarm=alarm))
        # Call pyRule
        if self.pyrule:
            self.pyrule(alarm=alarm)
