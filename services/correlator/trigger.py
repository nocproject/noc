# ---------------------------------------------------------------------
# Alarm trigger
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012, The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import logging

# NOC Modules
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)


class Trigger(object):
    def __init__(self, t):
        self.name = t.name
        # Condition
        self.condition = compile(t.condition, "<string>", "eval")
        self.time_pattern = t.time_pattern
        self.resource_group = t.resource_group
        # Action
        self.notification_group = t.notification_group
        self.template = t.template
        self.handler = get_handler(t.handler)

    def match(self, alarm):
        """
        Check event matches trigger condition
        """
        return (
            eval(self.condition, {}, {"alarm": alarm, "re": re})
            and (self.time_pattern.match(alarm.timestamp) if self.time_pattern else True)
            and (
                str(self.resource_group.id) in alarm.managed_object.effective_service_groups
                if self.resource_group
                else True
            )
        )

    def call(self, alarm):
        if not self.match(alarm):
            return
        print(self.resource_group)
        logger.info("Calling trigger '%s'" % self.name)
        # Notify if necessary
        if self.notification_group and self.template:
            self.notification_group.notify(
                subject=self.template.render_subject(alarm=alarm),
                body=self.template.render_body(alarm=alarm),
            )
        # Call handler
        if self.handler:
            try:
                self.handler(alarm=alarm)
            except Exception as e:
                logger.error("Exception when calling AlarmTrigger handler: %s", e)
