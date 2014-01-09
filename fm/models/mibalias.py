# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIBAlias model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, UUIDField
## NOC modules
from noc.lib.prettyjson import to_json



class MIBAlias(Document):
    """
    MIB Aliases
    """
    meta = {
        "collection": "noc.mibaliases",
        "allow_inheritance": False
    }
    rewrite_mib = StringField(unique=True)
    to_mib = StringField()
    uuid = UUIDField(binary=True)

    ## Lookup cache
    cache = None

    def __unicode__(self):
        return u"%s -> %s" % (self.rewrite_mib, self.to_mib)

    @classmethod
    def rewrite(cls, name):
        """
        Rewrite OID with alias if any
        """
        if cls.cache is None:
            # Initialize cache
            cls.cache = dict((a.rewrite_mib, a.to_mib)
                             for a in cls.objects.all())
        # Lookup
        if "::" in name:
            mib, rest = name.split("::", 1)
            return "%s::%s" % (cls.cache.get(mib, mib), rest)
        return cls.cache.get(name, name)

    def get_json_path(self):
        return "%s.json" % self.rewrite_mib.replace(":", "_")

    def to_json(self):
        return to_json({
            "rewrite_mib": self.rewrite_mib,
            "to_mib": self.to_mib,
            "uuid": self.uuid
        }, order=["rewrite_mib", "to_mib", "uuid"])
