## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MAC Database
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.nosql import (Document, StringField, ForeignKeyField,
                           PlainReferenceField, DateTimeField,
                           IntField)
from interface import Interface
from noc.sa.models.managedobject import ManagedObject
from maclog import MACLog
from noc.lib.mac import MAC


class MACDB(Document):
    """
    Customer MAC address database
    """
    meta = {
        "collection": "noc.macs",
        "allow_inheritance": False,
        "indexes": ["mac", "interface"]
    }
    # Todo: Add Validation
    mac = StringField()
    vlan = IntField()
    managed_object = ForeignKeyField(ManagedObject)
    interface = PlainReferenceField(Interface)
    last_changed = DateTimeField()

    def __unicode__(self):
        return self.mac

    def save(self):
        self.mac = MAC(self.mac)
        if not self.last_changed:
            self.last_changed = datetime.datetime.now()
        super(MACDB, self).save()

    @classmethod
    def submit(cls, mac, vlan, interface, timestamp=None):
        """
        Submit mac to database
        Returns True if database been changed
        :param cls:
        :param mac:
        :param interface:
        :param timestamp:
        :return:
        """
        if not timestamp:
            timestamp = datetime.datetime.now()
        managed_object = interface.managed_object
        mac = MAC(mac)
        m = MACDB.objects.filter(mac=mac).first()
        if m:
            if (managed_object != m.managed_object or
                interface != m.interface or vlan != m.vlan):
                # Database change, write history
                MACLog(
                    timestamp=m.last_changed,
                    mac=mac,
                    vlan=m.vlan,
                    managed_object_name=m.managed_object.name,
                    interface_name=m.interface.name
                ).save()
                m.vlan = vlan
                m.managed_object = managed_object
                m.interface = interface
                m.last_changed = timestamp
                m.save()
                return True
            else:
                return False
        else:
            MACDB(
                mac=mac,
                vlan=vlan,
                managed_object=managed_object,
                interface=interface,
                last_changed=timestamp
            ).save()
            return True
