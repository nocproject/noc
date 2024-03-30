# ---------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import logging

# Python modules
from noc.core.debug import error_report
from noc.core.handler import get_handler


class Trigger(object):
    def __init__(self, t, handler=None):
        self.name = t.name
        # Condition
        self.condition = compile(t.condition, "<string>", "eval")
        self.time_pattern = t.time_pattern
        self.resource_group = t.resource_group
        # Action
        self.notification_group = t.notification_group
        self.template = t.template
        self.handler = get_handler(handler) if handler else None

    def match(self, event):
        """
        Check event matches trigger condition
        """
        return (
            eval(self.condition, {}, {"event": event, "re": re})
            and (self.time_pattern.match(event.timestamp) if self.time_pattern else True)
            and (
                str(self.resource_group.id) in event.managed_object.effective_service_groups
                if self.resource_group
                else True
            )
        )

    def call(self, event):
        if not self.match(event):
            return
        logging.debug("Calling trigger '%s'" % self.name)
        # Notify if necessary
        if self.notification_group and self.template:
            subject = {}
            body = {}
            for lang in self.notification_group.languages:
                s = event.subject
                b = event.body
                subject[lang] = self.template.render_subject(
                    LANG=lang, event=event, subject=s, body=b
                )
                body[lang] = self.template.render_body(LANG=lang, event=event, subject=s, body=b)
            self.notification_group.notify(subject=subject, body=body)
        # Call Handler
        if self.handler:
            try:
                self.handler(event)
            except Exception:
                error_report()
