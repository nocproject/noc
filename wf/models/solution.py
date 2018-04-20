# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Solution model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql


class Solution(nosql.Document):
    meta = {
        "collection": "noc.wf.solutions",
        "allow_inheritance": False
    }

    name = nosql.StringField()
    version = nosql.IntField(default=1)
    is_active = nosql.BooleanField(default=False)
    description = nosql.StringField()

    def __unicode__(self):
        return "%s v%s" % (self.name, self.version)

    @classmethod
    def get_active(cls, name):
        """
        Get last version of active solution
        :param cls:
        :param name: Solution name
        :return: Solution or None
        """
        return cls.objects.filter(name=name, is_active=True)\
            .order_by("-version").first()
