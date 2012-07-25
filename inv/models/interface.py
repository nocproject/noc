## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import Document, ForeignKeyField, StringField,\
    IntField, BooleanField, PlainReferenceField
from interfaceprofile import InterfaceProfile
from noc.sa.models import ManagedObject
from noc.sa.interfaces import MACAddressParameter


class Interface(Document):
    """
    Interfaces
    """
    meta = {
        "collection": "noc.interfaces",
        "allow_inheritance": False,
        "indexes": [
            ("managed_object", "name"),
            "mac"
        ]
    }
    managed_object = ForeignKeyField(ManagedObject)
    name = StringField()  # Normalized via Profile.convert_interface_name
    type = StringField(choices=[(x, x) for x in
                                    ["physical", "SVI", "aggregated",
                                     "loopback", "management",
                                     "null", "tunnel", "other", "unknown"]])
    description = StringField(required=False)
    ifindex = IntField(required=False)
    mac = StringField(required=False)
    aggregated_interface = PlainReferenceField("self", required=False)
    is_lacp = BooleanField(default=False)
    # @todo: admin status + oper status
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)
    # profile locked on manual user change
    profile_locked = BooleanField(required=False, default=False)

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name, self.name)

    def save(self, *args, **kwargs):
        self.name = self.managed_object.profile.convert_interface_name(self.name)
        if self.mac:
            self.mac = MACAddressParameter().clean(self.mac)
        super(Interface, self).save(*args, **kwargs)

    @property
    def link(self):
        """
        Return Link instance or None
        :return:
        """
        return Link.objects.filter(interfaces=self.id).first()

    @property
    def is_linked(self):
        """
        Check interface is linked
        :returns: True if interface is linked, False otherwise
        """
        return self.link is not None

    def unlink(self):
        """
        Remove existing link.
        Raise ValueError if interface is not linked
        """
        link = self.link
        if link is None:
            raise ValueError("Interface is not linked")
        if link.is_ptp:
            link.delete()
        else:
            raise ValueError("Cannot unlink non p-t-p link")

    def link_ptp(self, other):
        """
        Create p-t-p link with other interface
        Raise ValueError if either of interface already connected.
        :type other: Interface
        :returns: Link instance
        """
        if self.is_linked or other.is_linked:
            raise ValueError("Already linked")
        if self.id == other.id:
            raise ValueError("Cannot link with self")
        link = Link(interfaces=[self, other])
        link.save()
        return link

    @classmethod
    def get_interface(cls, s):
        """
        Parse <managed object>@<interface> string
        and return interface instance or None
        """
        if "@" not in s:
            raise ValueError("Invalid interface: %s" % s)
        o, i = s.rsplit("@", 1)
        # Get managed object
        try:
            mo = ManagedObject.objects.get(name=o)
        except ManagedObject.DoesNotExist:
            raise ValueError("Invalid manged object: %s" % o)
        # Normalize interface name
        i = mo.profile.convert_interface_name(i)
        # Look for interface
        iface = Interface.objects.filter(managed_object=mo.id,
            name=i).first()
        return iface

    @property
    def subinterface_set(self):
        return SubInterface.objects.filter(interface=self.id)


## Avoid circular references
from subinterface import SubInterface
from link import Link
