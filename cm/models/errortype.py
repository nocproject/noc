# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Error Types
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField
## NOC modules
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path
from noc.lib.collection import collection


@collection
class ErrorType(Document):
    meta = {
        "collection": "noc.errortypes",
        "json_collection": "cm.errortypes"
    }
    name = StringField(unique=True)
    uuid = UUIDField(binary=True, unique=True)
    description = StringField()
    subject_template = StringField()
    body_template = StringField()

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def to_json(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "subject_template": self.subject_template,
            "body_template": self.body_template
        }
        if self.description:
            r["description"] = self.description
        return to_json(r, order=["name", "$collection",
                                 "uuid", "description",
                                 "subject_template", "body_template"])
