# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SyntaxAlias model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql


class SyntaxAlias(nosql.Document):
    meta = {
        "collection": "noc.syntaxaliases",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True, required=True)
    syntax = nosql.DictField(required=False)
    is_builtin = nosql.BooleanField(default=False)
    # Lookup cache
    cache = None

    def __unicode__(self):
        return self.name

    @classmethod
    def rewrite(cls, name, syntax):
        if cls.cache is None:
            cls.cache = dict((o.name, o.syntax)
                             for o in cls.objects.all())
        return cls.cache.get(name, syntax)
