# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CloneClassificationRule management
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from mongoengine.document import Document
from mongoengine import fields
## NOC modules
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json


class CloneClassificationRule(Document):
    """
    Classification rules cloning
    """
    meta = {
        "collection": "noc.cloneclassificationrules",
        "allow_inheritance": False,
        "json_collection": "fm.cloneclassificationrules"
    }

    name = fields.StringField(unique=True)
    uuid = fields.UUIDField(binary=True)
    re = fields.StringField(default="^.*$")
    key_re = fields.StringField(default="^.*$")
    value_re = fields.StringField(default="^.*$")
    rewrite_from = fields.StringField()
    rewrite_to = fields.StringField()

    def __unicode__(self):
        return self.name

    def to_json(self):
        return to_json({
            "name": self.name,
            "uuid": self.uuid,
            "re": self.re,
            "key_re": self.key_re,
            "value_re": self.value_re,
            "rewrite_from": self.rewrite_from,
            "rewrite_to": self.rewrite_to
        }, order=["name", "uuid", "re", "key_re", "value_re",
                  "rewrite_from", "rewrite_to"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
