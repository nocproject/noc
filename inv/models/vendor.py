## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, URLField
## NOC modules
from noc.lib.escape import json_escape as q


class Vendor(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.vendors",
        "allow_inheritance": False,
    }

    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    site = URLField(required=False)

    def __unicode__(self):
        return self.name

    def to_json(self):
        r = [
            "[",
            "    {",
            "        \"name\": \"%s\"," % q(self.name),
            "        \"site\": \"%s\"" % q(self.site),
            "    }",
            "]"
        ]
        return "\n".join(r)