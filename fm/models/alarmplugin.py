# ---------------------------------------------------------------------
# AlarmPlugin model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Dict

# Third-party modules
from mongoengine import fields
from mongoengine.document import EmbeddedDocument


class AlarmPlugin(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    name = fields.StringField()
    config = fields.DictField(default={})

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
        }
        if self.config:
            for key in self.config:
                r[key] = self.config[key]
        return r
