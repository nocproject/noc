# ---------------------------------------------------------------------
# AlarmLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DateTimeField, StringField


class AlarmLog(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    timestamp = DateTimeField()
    from_status = StringField(max_length=1, regex=r"^[AC]$", required=True)
    to_status = StringField(max_length=1, regex=r"^[AC]$", required=True)
    message = StringField()
    source = StringField(required=False)
    user = StringField(required=False)
    document_id = StringField(required=False)

    def __str__(self):
        return "%s [%s -> %s]: %s" % (
            self.timestamp,
            self.from_status,
            self.to_status,
            self.message,
        )
