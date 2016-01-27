# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology received from external NRI system
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, ObjectIdField


class ExtNRILink(Document):
    """
    Links received from external NRI system via ETL.
    When *xnri* topology discovery is enabled
    interface discovery pre-populating links using this table

    Profile's split_interface() method is used to convert
    normalized interface name to (chassis, slot, port) form,
    while join_interface method is used to merge them back
    to normalized interface name
    """
    # Source managed object
    src_mo = IntField()
    # Source managed object's chassis number, starting with 1
    # 1 for single-chassis system
    src_chassis = IntField(default=1)
    # Source slot number, starting with 0
    src_slot = IntField(default=0)
    # Source port number, starting with 1
    src_port = IntField(default=1)
    # Destination managed object
    dst_mo = IntField()
    # Destination managed object's chassis number, starting with 1
    # 1 for single-chassis system
    dst_chassis = IntField(default=1)
    # Destination slot number
    dst_slot = IntField(default=0)
    # Destination port number
    dst_port = IntField(default=1)
    # Created link id
    link = ObjectIdField()
