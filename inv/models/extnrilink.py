# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Topology received from external NRI system
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.queryset import Q
from mongoengine.fields import IntField, ObjectIdField, StringField, BooleanField


class ExtNRILink(Document):
    """
    Links received from external NRI system via ETL.
    When *nri* topology discovery is enabled
    interface discovery pre-populating links using this table
    """
    meta = {
        "collection": "noc.extnrilinks",
        "strict": False,
        "auto_create_index": False,
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
    # Do not try to create NRI link
    ignore = BooleanField(default=False)

    @classmethod
    def get_connected(self, mo):
        """
        Return managed objects connected to mo
        """
        from noc.sa.models.managedobject import ManagedObject
        if hasattr(mo, "id"):
            mo = mo.id
        r = set()
        for n in ExtNRILink.objects.filter(Q(src_mo=mo) | Q(dst_mo=mo)):
            if n.src_mo == mo:
                rmo = n.dst_mo
            else:
                rmo = n.src_mo
            m = ManagedObject.get_by_id(rmo)
            if m:
                r.add(m)
        return r
