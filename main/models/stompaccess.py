## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## StompAccess model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, ForeignKeyField, StringField,
                           BooleanField, ListField)
from noc.main.models.prefixtable import PrefixTable


class StompAccess(Document):
    meta = {
        "collection": "noc.stomp_access",
        "allow_inheritance": False,
        "indexes": ["user"]
    }

    user = StringField()
    password = StringField()
    prefix_table = ForeignKeyField(PrefixTable)

    def unicode(self):
        return self.user

    @classmethod
    def authenticate(cls, user, password, address):
        """
        Authenticate user against access database
        :param user:
        :param password:
        :param address:
        :rtype: bool
        :return: True if user is authenticated, False otherwise
        """
        sa = cls.objects.filter(user=user).first()
        if not sa:
            return False  # User does not exists
        # @todo: Hashing
        if sa.password != password:
            return False  # Invalid password
        if sa.prefix_table and not sa.prefix_table.match(address):
            return False  # Invalid source address
        return True  # All checks are passed
