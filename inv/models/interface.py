<<<<<<< HEAD
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField,
                                ListField, DateTimeField, ReferenceField)
from pymongo import ReadPreference

# NOC Modules
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.base import MACAddressParameter
=======
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
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces import MACAddressParameter
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.main.models.resourcestate import ResourceState
from noc.project.models.project import Project
from noc.vc.models.vcdomain import VCDomain
<<<<<<< HEAD
from noc.sa.models.service import Service
from noc.core.model.decorator import on_delete
from .interfaceprofile import InterfaceProfile
from .coverage import Coverage
=======
from noc.lib.solutions import get_probe_config
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


INTERFACE_TYPES = (IGetInterfaces.returns
                   .element.attrs["interfaces"]
                   .element.attrs["type"].choices)
INTERFACE_PROTOCOLS = (IGetInterfaces.returns
                       .element.attrs["interfaces"]
                       .element.attrs["enabled_protocols"]
                       .element.choices)


<<<<<<< HEAD
logger = logging.getLogger(__name__)


@on_delete
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class Interface(Document):
    """
    Interfaces
    """
    meta = {
        "collection": "noc.interfaces",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            ("managed_object", "name"),
            "mac",
            ("managed_object", "ifindex"),
            "service",
            "aggregated_interface"
=======
        "allow_inheritance": False,
        "indexes": [
            ("managed_object", "name"),
            "mac",
            ("managed_object", "ifindex")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    profile = PlainReferenceField(InterfaceProfile,
                                  default=InterfaceProfile.get_default_profile)
=======
    # @todo: admin status + oper status
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    # profile locked on manual user change
    profile_locked = BooleanField(required=False, default=False)
    #
    project = ForeignKeyField(Project)
    state = ForeignKeyField(ResourceState)
    vc_domain = ForeignKeyField(VCDomain)
<<<<<<< HEAD
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
    # External NRI interface name
    nri_name = StringField()
    #
    service = ReferenceField(Service)
=======
    # Coverage
    coverage = PlainReferenceField(Coverage)
    technologies = ListField(StringField())
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    PROFILE_LINK = "profile"

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name, self.name)

    def save(self, *args, **kwargs):
<<<<<<< HEAD
        if not hasattr(self, "_changed_fields") or "name" in self._changed_fields:
            self.name = self.managed_object.get_profile().convert_interface_name(self.name)
        if (not hasattr(self, "_changed_fields") or "mac" in self._changed_fields) and self.mac:
            self.mac = MACAddressParameter().clean(self.mac)
        try:
            super(Interface, self).save(*args, **kwargs)
        except Exception as e:
            raise ValueError("%s: %s" % (e.__doc__, e.message))
        if not hasattr(self, "_changed_fields") or "service" in self._changed_fields:
            ServiceSummary.refresh_object(self.managed_object)

    def on_delete(self):
=======
        self.name = self.managed_object.profile.convert_interface_name(self.name)
        if self.mac:
            self.mac = MACAddressParameter().clean(self.mac)
        super(Interface, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Remove all subinterfaces
        for si in self.subinterface_set.all():
            si.delete()
        # Unlink
        link = self.link
        if link:
            self.unlink()
        # Flush MACDB
        MACDB.objects.filter(interface=self.id).delete()
<<<<<<< HEAD
=======
        # Remove interface
        super(Interface, self).delete(*args, **kwargs)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    @property
    def link(self):
        """
        Return Link instance or None
        :return:
        """
<<<<<<< HEAD
        if self.type == "aggregated":
            q = {
                "interfaces__in": [self.id] + [i.id for i in self.lag_members]
            }
        else:
            q = {
                "interfaces": self.id
            }
        return Link.objects.filter(**q).first()
=======
        return Link.objects.filter(interfaces=self.id).first()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    @property
    def is_linked(self):
        """
        Check interface is linked
        :returns: True if interface is linked, False otherwise
        """
<<<<<<< HEAD
        if self.type == "aggregated":
            q = {
                "interfaces": {
                    "$in": [self.id] + [i.id for i in self.lag_members]
                }
            }
        else:
            q = {"interfaces": self.id}
        return bool(Link._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        ).find_one(q))
=======
        return bool(Link.objects.filter(interfaces=self.id).limit(1).count())
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def unlink(self):
        """
        Remove existing link.
        Raise ValueError if interface is not linked
        """
        link = self.link
        if link is None:
            raise ValueError("Interface is not linked")
<<<<<<< HEAD
        if link.is_ptp or link.is_lag:
=======
        if link.is_ptp:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            link.delete()
        else:
            raise ValueError("Cannot unlink non p-t-p link")

    def link_ptp(self, other, method=""):
        """
        Create p-t-p link with other interface
        Raise ValueError if either of interface already connected.
<<<<<<< HEAD
        :param other: Other Iface for link
        :param method: Linking method
        :type other: Interface
        :returns: Link instance
        """
        def link_mismatched_lag(agg, phy):
            """
            Try to link LAG to physical interface
            :param agg:
            :param phy:
            :return:
            """
            l_members = [i for i in agg.lag_members if i.oper_status]
            if len(l_members) > 1:
                raise ValueError("More then one active interface in LAG")
            link = Link(
                interfaces=l_members + [phy],
                discovery_method=method
            )
            link.save()
            return link

=======
        :type other: Interface
        :returns: Link instance
        """
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                link = Link(
                    interfaces=[self, other],
                    discovery_method=method
                )
                link.save()
                return link
            elif other.type == "aggregated" and other.profile.allow_lag_mismatch:
                return link_mismatched_lag(other, self)
=======
                link = Link(interfaces=[self, other],
                    discovery_method=method)
                link.save()
                return link
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                    link = Link(
                        interfaces=l_members + r_members,
                        discovery_method=method
                    )
=======
                    link = Link(interfaces=l_members + r_members,
                        discovery_method=method)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    link.save()
                    return link
                else:
                    return
<<<<<<< HEAD
            elif self.profile.allow_lag_mismatch:
                return link_mismatched_lag(self, other)
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        i = mo.get_profile().convert_interface_name(i)
        # Look for interface
        iface = Interface.objects.filter(managed_object=mo.id,
                                         name=i).first()
=======
        i = mo.profile.convert_interface_name(i)
        # Look for interface
        iface = Interface.objects.filter(managed_object=mo.id,
            name=i).first()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return iface

    @property
    def subinterface_set(self):
<<<<<<< HEAD
        from .subinterface import SubInterface
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

<<<<<<< HEAD
    @property
    def status(self):
        """
        Returns interface status in form of
        Up/100/Full
        """
        def humanize_speed(speed):
            if not speed:
                return "-"
            for t, n in [(1000000, "G"), (1000, "M"), (1, "k")]:
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
                not self.oper_status_change or self.oper_status_change < now):
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

    @property
    def parent(self):
        """
        Returns aggregated interface for LAG or
        self for non-aggregated interface
        """
        if self.aggregated_interface:
            return self.aggregated_interface
        else:
            return self

    def get_profile(self):
        if self.profile:
            return self.profile
        return InterfaceProfile.get_default_profile()


# Avoid circular references
from noc.sa.models.servicesummary import ServiceSummary
from .link import Link
from .macdb import MACDB
=======
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
        try:
            return self.managed_object.get_probe_config(config)
        except ValueError:
            pass
        # Fallback to interface profile
        return self.profile.get_probe_config(config)


## Avoid circular references
from subinterface import SubInterface
from link import Link
from macdb import MACDB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
