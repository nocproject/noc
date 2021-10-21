# ---------------------------------------------------------------------
# DataSource model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import StringField, DictField


class DataSource(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    datasource = StringField()
    search = DictField()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.datasource == other.datasource
            and self.search == other.search
        )

    @property
    def json_data(self):
        return {
            "name": self.name,
            "datasource": self.datasource,
            "search": {ss: self.search[ss] for ss in self.search},
        }
