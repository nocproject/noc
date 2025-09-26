# ---------------------------------------------------------------------
# MAC Database
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, DateTimeField

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from .interface import Interface
from noc.sa.models.managedobject import ManagedObject
from .maclog import MACLog
from noc.core.mac import MAC


class MACDB(Document):
    """
    Customer MAC address database
    """

    meta = {
        "collection": "noc.macs",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["mac", "interface"],
    }
    # Todo: Add Validation
    mac = StringField()
    vlan = IntField()
    managed_object = ForeignKeyField(ManagedObject)
    interface = PlainReferenceField(Interface)
    last_changed = DateTimeField()

    def __str__(self):
        return self.mac

    def save(self, *args, **kwargs):
        self.mac = MAC(self.mac)
        if not self.last_changed:
            self.last_changed = datetime.datetime.now()
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            raise ValueError("%s: %s" % (e.__doc__, e.message))

    @classmethod
    def submit(cls, mac, vc_domain, vlan, interface, timestamp=None):
        """
        Submit mac to database
        Returns True if database been changed
        :param cls:
        :param mac:
        :param vc_domain
        :param vlan
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
            if managed_object != m.managed_object or interface != m.interface or vlan != m.vlan:
                # Database change, write history
                MACLog(
                    timestamp=m.last_changed,
                    mac=mac,
                    vc_domain_name=vc_domain.name if vc_domain else None,
                    vlan=m.vlan,
                    managed_object_name=m.managed_object.name,
                    interface_name=m.interface.name,
                ).save()
                m.vlan = vlan
                m.managed_object = managed_object
                m.interface = interface
                m.last_changed = timestamp
                m.save()
                return True
            return False
        MACDB(
            mac=mac,
            vc_domain=vc_domain,
            vlan=vlan,
            managed_object=managed_object,
            interface=interface,
            last_changed=timestamp,
        ).save()
        return True
