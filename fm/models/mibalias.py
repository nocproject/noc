# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIBAlias model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql


class MIBAlias(nosql.Document):
    """
    MIB Aliases
    """
    meta = {
        "collection": "noc.mibaliases",
        "allow_inheritance": False
    }
    rewrite_mib = nosql.StringField(unique=True)
    to_mib = nosql.StringField()
    is_builtin = nosql.BooleanField(default=False)

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
