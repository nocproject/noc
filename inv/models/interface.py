## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.nosql import (Document, ForeignKeyField, StringField,
    IntField, BooleanField, PlainReferenceField, ListField)
from interfaceprofile import InterfaceProfile
from coverage import Coverage
from noc.sa.models import ManagedObject
from noc.sa.interfaces import MACAddressParameter
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.vc.models.vcdomain import VCDomain
from noc.lib.solutions import get_probe_config


INTERFACE_TYPES = (IGetInterfaces.returns
                   .element.attrs["interfaces"]
                   .element.attrs["type"].choices)
INTERFACE_PROTOCOLS = (IGetInterfaces.returns
                       .element.attrs["interfaces"]
                       .element.attrs["enabled_protocols"]
                       .element.choices)


class Interface(Document):
    """
    Interfaces
    """
    meta = {
        "collection": "noc.interfaces",
        "allow_inheritance": False,
        "indexes": [
            ("managed_object", "name"),
            "mac",
            ("managed_object", "ifindex")
        ]
    }
    managed_object = ForeignKeyField(ManagedObject)
    name = StringField()  # Normalized via Profile.convert_interface_name
    type = StringField(choices=[(x, x) for x in INTERFACE_TYPES])
    description = StringField(required=False)
    ifindex = IntField(required=False)
    mac = StringField(required=False)
    aggregated_interface = PlainReferenceField("self", required=False)
    enabled_protocols = ListField(StringField(
        choices=[(x, x) for x in INTERFACE_PROTOCOLS]
    ), default=[])
    # @todo: admin status + oper status
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)
    # profile locked on manual user change
    profile_locked = BooleanField(required=False, default=False)
    #
    project = ForeignKeyField(Project)
    state = ForeignKeyField(ResourceState)
    vc_domain = ForeignKeyField(VCDomain)
    # Coverage
    coverage = PlainReferenceField(Coverage)
    technologies = ListField(StringField())

    PROFILE_LINK = "profile"

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name, self.name)

    def save(self, *args, **kwargs):
        self.name = self.managed_object.profile.convert_interface_name(self.name)
        if self.mac:
            self.mac = MACAddressParameter().clean(self.mac)
        super(Interface, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Remove all subinterfaces
        for si in self.subinterface_set.all():
            si.delete()
        # Unlink
        link = self.link
        if link:
            self.unlink()
        # Flush MACDB
        MACDB.objects.filter(interface=self.id).delete()
        # Remove interface
        super(Interface, self).delete(*args, **kwargs)

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
        return bool(Link.objects.filter(interfaces=self.id).limit(1).count())

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

    def link_ptp(self, other, method=""):
        """
        Create p-t-p link with other interface
        Raise ValueError if either of interface already connected.
        :type other: Interface
        :returns: Link instance
        """
        # Try to check existing LAG
        el = Link.objects.filter(interfaces=self.id).first()
        if el and other not in el.interfaces:
            el = None
        if (self.is_linked or other.is_linked) and not el:
            raise ValueError("Already linked")
        if self.id == other.id:
            raise ValueError("Cannot link with self")
        if self.type in ("physical", "management"):
            if other.type in ("physical", "management"):
                # Refine LAG
                if el:
                    left_ifaces = [i for i in el.interfaces if i not in (self, other)]
                    if left_ifaces:
                        el.interfaces = left_ifaces
                        el.save()
                    else:
                        el.delete()
                #
                link = Link(interfaces=[self, other],
                    discovery_method=method)
                link.save()
                return link
            else:
                raise ValueError("Cannot connect %s interface to %s" % (
                    self.type, other.type))
        elif self.type == "aggregated":
            # LAG
            if other.type == "aggregated":
                # Check LAG size match
                # Skip already linked members
                l_members = [i for i in self.lag_members if not i.is_linked]
                r_members = [i for i in other.lag_members if not i.is_linked]
                if len(l_members) != len(r_members):
                    raise ValueError("LAG size mismatch")
                # Create link
                if l_members:
                    link = Link(interfaces=l_members + r_members,
                        discovery_method=method)
                    link.save()
                    return link
                else:
                    return
            else:
                raise ValueError("Cannot connect %s interface to %s" % (
                    self.type, other.type))
        raise ValueError("Cannot link")

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

    @property
    def lag_members(self):
        if self.type != "aggregated":
            raise ValueError("Cannot net LAG members for not-aggregated interface")
        return Interface.objects.filter(aggregated_interface=self.id)

    def get_probe_config(self, config):
        # Get via solutions
        try:
            return get_probe_config(self, config)
        except ValueError:
            pass
        # Fallback
        if config == "interface__name":
            return self.name
        elif config == "interface__ifindex":
            if self.ifindex is None:
                raise ValueError("No ifindex for %s" % self)
            else:
                return self.ifindex
        elif config == "address":
            return self.managed_object.address
        elif config == "snmp__ro":
            if self.managed_object.snmp_ro is None:
                raise ValueError("No snmp ro community for %s" % self)
            else:
                return self.managed_object.snmp_ro
        raise ValueError("Invalid config '%s'" % config)


## Avoid circular references
from subinterface import SubInterface
from link import Link
from macdb import MACDB
