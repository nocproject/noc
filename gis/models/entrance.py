# ---------------------------------------------------------------------
# Entrance object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, IntField


class Entrance(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    number = StringField()
    # Floors
    first_floor = IntField()
    last_floor = IntField()
    first_home = StringField()
    last_home = StringField()
    # @todo: Managing company

    def __str__(self):
        return self.number
