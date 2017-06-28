# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MAC Database
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
from noc.lib.nosql import (Document, StringField, ForeignKeyField,
                           PlainReferenceField, DateTimeField,
                           IntField)
from interface import Interface
from noc.sa.models.managedobject import ManagedObject
from noc.vc.models import VCDomain
from maclog import MACLog
from noc.core.mac import MAC


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
    vc_domain = ForeignKeyField(VCDomain, required=False)
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
        try:
            super(MACDB, self).save()
        except Exception as e:
            raise ValueError("%s: %s" % (e.__doc__, e.message))

    @classmethod
    def submit(cls, mac, vc_domain, vlan, interface, timestamp=None):
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
        vcd = vc_domain.id if vc_domain else None
        m = MACDB.objects.filter(mac=mac, vc_domain=vcd).first()
        if m:
            if (managed_object != m.managed_object or
                interface != m.interface or vlan != m.vlan):
                # Database change, write history
                MACLog(
                    timestamp=m.last_changed,
                    mac=mac,
                    vc_domain_name=vc_domain.name if vc_domain else None,
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
                vc_domain=vc_domain,
                vlan=vlan,
                managed_object=managed_object,
                interface=interface,
                last_changed=timestamp
            ).save()
            return True
