# ---------------------------------------------------------------------
# AlarmRootCauseCondition model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, IntField, DictField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField


class AlarmRootCauseCondition(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    name = StringField(required=True)
    root = PlainReferenceField("fm.AlarmClass")
    window = IntField(required=True)
    condition = StringField(default="True")
    match_condition = DictField(required=True)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and (
                (self.root is None and other.root is None)
                or (self.root and other.root and self.root.id == other.root.id)
            )
            and self.window == other.window
            and self.condition == other.condition
            and self.match_condition == other.match_condition
        )

    @property
    def json_data(self):
        r = {"name": self.name, "root__name": self.root.name, "window": self.window}
        if self.condition:
            r["condition"] = self.condition
        r["match_condition"] = {}
        for key in self.match_condition:
            r["match_condition"][key] = self.match_condition[key]
        return r
