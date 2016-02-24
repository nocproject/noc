# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology received from external NRI system
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, ObjectIdField, StringField


class ExtNRILink(Document):
    """
    Links received from external NRI system via ETL.
    When *nri* topology discovery is enabled
    interface discovery pre-populating links using this table
    """
    meta = {
        "collection": "noc.extnrilinks",
        "allow_inheritance": False,
        "indexes": ["src_mo", "dst_mo", "link"]
    }
    # Source managed object (NOC's ManagedObject.id)
    src_mo = IntField()
    # Source interface name in remote system notation
    src_interface = StringField()
    # Destination managed object (NOC's ManagedObject.id)
    dst_mo = IntField()
    # Source interface name in remote system notation
    dst_interface = StringField()
    # Created link id
    link = ObjectIdField()
    # Mapping warnings
    warn = StringField(required=False)
    # NRI link comparison errors
    error = StringField(required=False)
