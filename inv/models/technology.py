## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Technology
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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


class Technology(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.technologies",
        "allow_inheritance": False,
        "json_collection": "inv.technologies"
    }

    # Group | Name
    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()

    def __unicode__(self):
        return self.name

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def to_json(self):
        r = {
            "name": self.name,
            "uuid": self.uuid
        }
        if self.description:
            r["description"] = self.description
        return to_json(r, order=["name", "uuid", "description"])
