# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OIDAlias model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC project
import noc.lib.nosql as nosql


class OIDAlias(nosql.Document):
    meta = {
        "collection": "noc.oidaliases",
        "allow_inheritance": False
    }

    rewrite_oid = nosql.StringField(unique=True)
    to_oid = nosql.StringField()
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)

    ## Lookup cache
    cache = None

    def __unicode__(self):
        return u"%s -> %s" % (self.rewrite_oid, self.to_oid)

    @classmethod
    def rewrite(cls, oid):
        """
        Rewrite OID with alias if any
        """
        if cls.cache is None:
            # Initialize cache
            cls.cache = dict((a.rewrite_oid, a.to_oid.split("."))
                             for a in cls.objects.all())
        # Lookup
        l_oid = oid.split(".")
        rest = []
        while l_oid:
            c_oid = ".".join(l_oid)
            try:
                a_oid = cls.cache[c_oid]
                # Found
                return ".".join(a_oid + rest)
            except KeyError:
                rest = [l_oid.pop()] + rest
        # Not found
        return oid
