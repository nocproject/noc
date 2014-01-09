# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Trigger
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
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

    def match(self, event):
        """
        Check event matches trigger condition
        """
        return (eval(self.condition, {}, {"event": event, "re": re}) and
                (self.time_pattern.match(event.timestamp) if self.time_pattern else True) and
                (self.selector.match(event.managed_object) if self.selector else True))

    def call(self, event):
        if not self.match(event):
            return
        logging.debug("Calling trigger '%s'" % self.name)
        # Notify if necessary
        if self.notification_group and self.template:
            subject = {}
            body = {}
            for lang in self.notification_group.languages:
                s = event.get_translated_subject(lang)
                b = event.get_translated_body(lang)
                subject[lang] = self.template.render_subject(LANG=lang,
                                                event=event, subject=s, body=b)
                body[lang] = self.template.render_body(LANG=lang,
                                                event=event, subject=s, body=b)
            self.notification_group.notify(subject=subject, body=body)
        # Call pyRule
        if self.pyrule:
            self.pyrule(event=event)
