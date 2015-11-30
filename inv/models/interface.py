## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
## NOC Modules
from noc.lib.nosql import (Document, ForeignKeyField, StringField,
    IntField, BooleanField, PlainReferenceField, ListField,
    DateTimeField)
from interfaceprofile import InterfaceProfile
from coverage import Coverage
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.vc.models.vcdomain import VCDomain
from noc.pm.models.probeconfig import probe_config


INTERFACE_TYPES = (IGetInterfaces.returns
                   .element.attrs["interfaces"]
                   .element.attrs["type"].choices)
INTERFACE_PROTOCOLS = (IGetInterfaces.returns
                       .element.attrs["interfaces"]
                       .element.attrs["enabled_protocols"]
                       .element.choices)


logger = logging.getLogger(__name__)


@probe_config
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
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)
    # profile locked on manual user change
    profile_locked = BooleanField(required=False, default=False)
    #
    project = ForeignKeyField(Project)
    state = ForeignKeyField(ResourceState)
    vc_domain = ForeignKeyField(VCDomain)
    # Current status
    admin_status = BooleanField(required=False)
    oper_status = BooleanField(required=False)
    oper_status_change = DateTimeField(required=False,
                                       default=datetime.datetime.now)
    full_duplex = BooleanField(required=False)
    in_speed = IntField(required=False)  # Input speed, kbit/s
    out_speed = IntField(required=False)  # Output speed, kbit/s
    bandwidth = IntField(required=False)  # Configured bandwidth, kbit/s
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
        from subinterface import SubInterface
        return SubInterface.objects.filter(interface=self.id)

    @property
    def lag_members(self):
        if self.type != "aggregated":
            raise ValueError("Cannot net LAG members for not-aggregated interface")
        return Interface.objects.filter(aggregated_interface=self.id)

    @property
    def effective_vc_domain(self):
        if self.type in ("null", "tunnel", "other", "unknown"):
            return None
        if self.vc_domain:
            return self.vc_domain
        if self.managed_object.vc_domain:
            return self.managed_object.vc_domain
        return VCDomain.get_default()

    def get_probe_config(self, config):
        if config == "interface__name":
            return self.name
        elif config == "interface__ifindex":
            if self.ifindex is None:
                raise ValueError("No ifindex for %s" % self)
            else:
                return self.ifindex
        try:
            return self.managed_object.get_probe_config(config)
        except ValueError:
            pass
        # Fallback to interface profile
        return self.profile.get_probe_config(config)

    @property
    def status(self):
        """
        Returns interface status in form of
        Up/100/Full
        """
        def humanize_speed(speed):
            if not speed:
                return "-"
            for t, n in [
                (1000000, "G"),
                (1000, "M"),
                (1, "k")
            ]:
                if speed >= t:
                    if speed // t * t == speed:
                        return "%d%s" % (speed // t, n)
                    else:
                        return "%.2f%s" % (float(speed) / t, n)
            return str(speed)

        s = [{
            True: "Up",
            False: "Down",
            None: "-"
        }[self.oper_status]]
        # Speed
        if self.oper_status:
            if self.in_speed and self.in_speed == self.out_speed:
                s += [humanize_speed(self.in_speed)]
            else:
                s += [
                    humanize_speed(self.in_speed),
                    humanize_speed(self.out_speed)
                ]
            s += [{
                True: "Full",
                False: "Half",
                None: "-"
            }[self.full_duplex]]
        else:
            s += ["-", "-"]
        return "/".join(s)

    def set_oper_status(self, status):
        """
        Set current oper status
        """
        if self.oper_status == status:
            return
        now = datetime.datetime.now()
        if self.oper_status != status and (
                    not self.oper_status_change or
                        self.oper_status_change < now
        ):
            self.update(oper_status=status, oper_status_change=now)
            if self.profile.status_change_notification:
                logger.debug(
                    "Sending status change notification to %s",
                    self.profile.status_change_notification.name
                )
                self.profile.status_change_notification.notify(
                    subject="[%s] Interface %s(%s) is %s" % (
                        self.managed_object.name, self.name,
                        self.description or "",
                        "up" if status else "down"
                    ),
                    body="Interface %s (%s) is %s" % (
                        self.name, self.description or "",
                        "up" if status else "down"
                    )
                )

## Avoid circular references
from link import Link
from macdb import MACDB
