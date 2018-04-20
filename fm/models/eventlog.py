# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# EventLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## EventLog model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine import document, fields

EVENT_STATE_CHOICES = [
    ("N", "New"),
    ("F", "Failed"),
    ("A", "Active"),
    ("S", "Archived")
]


class EventLog(document.EmbeddedDocument):
    meta = {
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
=======
        "allow_inheritance": False,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }
    timestamp = fields.DateTimeField()
    from_status = fields.StringField(
        max_length=1, choices=EVENT_STATE_CHOICES, required=True)
    to_status = fields.StringField(
        max_length=1, choices=EVENT_STATE_CHOICES, required=True)
    message = fields.StringField()

    def __unicode__(self):
        return u"%s [%s -> %s]: %s" % (self.timestamp, self.from_status,
                                       self.to_status, self.message)
