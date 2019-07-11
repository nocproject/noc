# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# EventLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine import document, fields

EVENT_STATE_CHOICES = [("N", "New"), ("F", "Failed"), ("A", "Active"), ("S", "Archived")]


@six.python_2_unicode_compatible
class EventLog(document.EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    timestamp = fields.DateTimeField()
    from_status = fields.StringField(max_length=1, choices=EVENT_STATE_CHOICES, required=True)
    to_status = fields.StringField(max_length=1, choices=EVENT_STATE_CHOICES, required=True)
    message = fields.StringField()

    def __str__(self):
        return "%s [%s -> %s]: %s" % (
            self.timestamp,
            self.from_status,
            self.to_status,
            self.message,
        )
