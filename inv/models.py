## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## models for "inventory" module
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import datetime
from collections import defaultdict
## NOC modules
from noc.lib.nosql import *
from noc.main.models import Style
from noc.sa.models import ManagedObject, ManagedObjectSelector
from noc.sa.interfaces import MACAddressParameter


class Vendor(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.vendors",
        "allow_inheritance": False,
    }
    
    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    site = URLField(required=False)
    
    def __unicode__(self):
        return self.name


class SocketAttribute(EmbeddedDocument):
    name = StringField()
    required = BooleanField(default=True)
    type = StringField(choices=[(x, x) for x in ("str", "int", "float")])
    default = StringField(required=False)
    
    def __unicode__(self):
        return self.name
    
    def __eq__(self, v):
        return (self.name == v.name and
                self.required == v.required and
                self.type == v.type and
                self.default == v.default)


class SocketCategory(Document):
    meta = {
        "collection": "noc.socket_categories",
        "allow_inheritance": False
    }
    
    name = StringField()
    parent = ObjectIdField(required=False)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = SocketCategory.objects.filter(name=p_name).first()
            if not p:
                p = SocketCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super(SocketCategory, self).save(*args, **kwargs)

    
class Socket(Document):
    meta = {
        "collection": "noc.sockets",
        "allow_inheritance": False
    }
    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    description = StringField(required=False)
    # Does the socket have distinguished male/female genders
    has_gender = BooleanField(default=True)
    # Can one female be connected to multiple males
    multi_connection = BooleanField(default=False)
    # When acting in "Male" role compatible with females of
    # following types (in addition to self type)
    m_compatible = ListField(StringField(), required=False)
    # When acting in "Feale" role compatible with males of
    # following types (in addition to self type)
    # @todo: Cannot refer to self
    f_compatible = ListField(StringField(), required=False)
    # Additional attributes set in model
    model_attributes = ListField(EmbeddedDocumentField(SocketAttribute),
                                 required=False)
    #
    category = ObjectIdField()
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = SocketCategory.objects.filter(name=c_name).first()
        if not c:
            c = SocketCategory(name=c_name)
            c.save()
        self.category = c.id
        super(Socket, self).save(*args, **kwargs)
    
    @property
    def short_name(self):
        return self.name.split(" | ")[-1]


class ModelCategory(Document):
    meta = {
        "collection": "noc.model_categories",
        "allow_inheritance": False
    }
    
    name = StringField()
    parent = ObjectIdField(required=False)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = ModelCategory.objects.filter(name=p_name).first()
            if not p:
                p = ModelCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super(ModelCategory, self).save(*args, **kwargs)


rx_range_check = re.compile(r"^[a-zA-Z0-9_]+:\d+\.\.\d+(,[a-zA-Z0-9_]+:\d+\.\.\d+)*$")
rx_range_exp = re.compile(r"^(?P<var_name>[a-zA-Z0-9_]+):(?P<min>\d+)\.\.(?P<max>\d+)$")

class ModelSocket(EmbeddedDocument):
    meta = {
        "allow_inheritance": False
    }
    name = StringField()
    type = PlainReferenceField(Socket)
    kind = StringField(max_length=1, choices=[(x, x) for x in ("M", "F")])
    # Socket range expression
    range = StringField(required=False)
    
    def __unicode__(self):
        return self.name
    
    def __eq__(self, v):
        try:
            return (self.name == v.name and
                    self.type._id == v.type._id and
                    self.kind == v.kind and
                    self.range == v.range
                    )
        except AttributeError:
            return False
    
    def iter_range(self):
        """
        Parse range expression
        """
        if not self.range:
            raise StopIteration
        vars = []
        mins = []
        maxes = []
        current = []
        for p in self.range.split(","):
            p = p.strip()
            match = rx_range_exp.match(p)
            assert match is not None
            var, min, max = match.groups()
            min = int(min)
            max = int(max)
            assert min<=max
            vars += [var]
            mins += [min]
            maxes += [max]
            current += [min]
        l = len(vars)
        while True:
            yield dict(zip(vars, current))
            j = l - 1
            while j >= 0:
                current[j] += 1
                if current[j] == maxes[j]:
                    for k in range(j, l):
                        current[k] == mins[k]
                    j -= 1
                else:
                    break
            if current > maxes:
                break
    
    @property
    def names(self):
        if not self.range:
            yield self.name
        else:
            for d in self.iter_range():
                n = self.name
                for k, v in d.items():
                    n = n.replace("{{%s}}" % k, str(v))
                    yield n


class Model(Document):
    meta = {
        "collection": "noc.models",
        "allow_inheritance": False
    }
    vendor = PlainReferenceField(Vendor)
    name = StringField(unique=True)
    is_builtin = BooleanField(default=False)
    description = StringField(required=False)
    part_number = StringField(required=False)
    part_number_aliases = ListField(StringField(), required=False)
    # Outer slots
    o_sockets = ListField(EmbeddedDocumentField(ModelSocket), required=False)
    # Inner slots
    i_sockets = ListField(EmbeddedDocumentField(ModelSocket), required=False)
    # Commutation slots
    c_sockets = ListField(EmbeddedDocumentField(ModelSocket), required=False)
    #
    category = ObjectIdField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = ModelCategory.objects.filter(name=c_name).first()
        if not c:
            c = ModelCategory(name=c_name)
            c.save()
        self.category = c.id
        super(Model, self).save(*args, **kwargs)
    
    @property
    def short_name(self):
        return self.name.split(" | ")[-1]

#class AttachedFile(EmbeddedDocument):
#    name = StringField()
#    file = FileField()
##   tags = 

##
## Network topology
##
class InterfaceProfile(Document):
    """
    Interface SLA profile and settings
    """
    meta = {
        "collection": "noc.interface_profiles",
        "allow_inheritance": False
    }
    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style)
    # Interface-level events processing
    link_events = StringField(
        required=True,
        choices=[
            ("I", "Ignore Events"),
            ("L", "Log events, do not raise alarms"),
            ("A", "Raise alarms")
        ],
        default="A"
    )

    def __unicode__(self):
        return self.name

    @classmethod
    def get_default_profile(cls):
        try:
            return cls._default_profile
        except AttributeError:
            cls._default_profile = cls.objects.filter(
                name="default").first()
            return cls._default_profile


class ForwardingInstance(Document):
    """
    Non-default forwarding instances
    """
    meta = {
        "collection": "noc.forwardinginstances",
        "allow_inheritance": False,
        "indexes": ["managed_object"]
    }
    managed_object = ForeignKeyField(ManagedObject)
    type = StringField(choices=[(x, x) for x in ("ip", "bridge", "VRF",
                                                 "VPLS", "VLL")],
                       default="ip")
    virtual_router = StringField(required=False)
    name = StringField()
    # VRF

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name,
                            self.name if self.name else "default")


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
    # admin status + oper status
    # is_ignored = BooleanField(default=False)
    profile = PlainReferenceField(InterfaceProfile,
        default=InterfaceProfile.get_default_profile)
    
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


class SubInterface(Document):
    meta = {
        "collection": "noc.subinterfaces",
        "allow_inheritance": False,
        "indexes": [
            "interface", "managed_object", "untagged_vlan", "tagged_vlans",
            "is_bridge", "is_ipv4", "is_ipv6"
        ]
    }
    interface = PlainReferenceField(Interface)
    managed_object = ForeignKeyField(ManagedObject)
    forwarding_instance = PlainReferenceField(ForwardingInstance, required=False)
    name = StringField()
    description = StringField(required=False)
    mac = StringField(required=False)
    vlan_ids = ListField(IntField(), default=[])
    is_ipv4 = BooleanField(default=False)
    is_ipv6 = BooleanField(default=False)
    is_mpls = BooleanField(default=False)
    is_bridge = BooleanField(default=False)
    ipv4_addresses = ListField(StringField(), default=[])
    ipv6_addresses = ListField(StringField(), default=[])
    iso_addresses = ListField(StringField(), default=[])
    is_isis = BooleanField(default=False)
    is_ospf = BooleanField(default=False)
    is_rsvp = BooleanField(default=False)
    is_ldp = BooleanField(default=False)
    is_rip = BooleanField(default=False)
    is_bgp = BooleanField(default=False)
    is_eigrp = BooleanField(default=False)
    untagged_vlan = IntField(required=False)
    tagged_vlans = ListField(IntField(), default=[])
    # ip_unnumbered_subinterface
    ifindex = IntField(required=False)

    def __unicode__(self):
        return "%s %s" % (self.interface.managed_object.name, self.name)


class Link(Document):
    """
    Network links.
    Always contains a list of 2*N references.
    2 - for fully resolved links
    2*N for unresolved N-link portchannel
    N, N > 2 - broadcast media
    """
    meta = {
        "collection": "noc.links",
        "allow_inheritance": False,
        "indexes": ["interfaces"]
    }

    interfaces = PlainReferenceListField(Interface)

    def __unicode__(self):
        return u"(%s)" % ", ".join([unicode(i) for i in self.interfaces])

    @property
    def is_ptp(self):
        """
        Check link is point-to-point link
        :return:
        """
        return len(self.interfaces) == 2

    @property
    def is_lag(self):
        """
        Check link is unresolved LAG
        :return:
        """
        if self.is_ptp:
            return True
        d = defaultdict(int)  # object -> count
        for i in self.interfaces:
            d[i.managed_object.id] += 1
        if len(d) != 2:
            return False
        k = d.keys()
        return d[k[0]] == d[k[1]]

    @property
    def is_broadcast(self):
        """
        Check link is broadcast media
        :return:
        """
        return not self.is_ptp and not self.is_lag

    def other(self, interface):
        """
        Return other interfaces of the link
        :param interface:
        :return:
        """
        return [i for i in self.interfaces if i.id != interface.id]

    def other_ptp(self, interface):
        """
        Return other interface of ptp link
        :param interface:
        :return:
        """
        return self.other(interface)[0]


class DiscoveryStatusInterface(Document):
    meta = {
        "collection": "noc.discovery.status.interface",
        "allow_inheritance": False,
        "indexes": [
            "managed_object",
            "next_check"
        ]
    }
    managed_object = ForeignKeyField(ManagedObject)
    last_check = DateTimeField(required=False)
    last_status = BooleanField(default=False)
    next_check = DateTimeField()

    @classmethod
    def reschedule(cls, object, ts, status=None):
        """
        Reschedule next interface check of object to time ts
        :param object: managed object
        :type object: ManagedObject
        :param ts: next check time
        :type ts: datetime.datetime
        """
        if isinstance(ts, int) or isinstance(ts, long):
            ts = datetime.datetime.now() + datetime.timedelta(seconds=ts)
        s = cls.objects.filter(managed_object=object.id).first()
        if s:
            s.next_check = ts
        else:
            s = cls(managed_object=object, next_check=ts)
        if status is not None:
            s.last_status = status
            s.last_check = datetime.datetime.now()
        s.save()


class DiscoveryStatusIP(Document):
    meta = {
        "collection": "noc.discovery.status.ip",
        "allow_inheritance": False,
        "indexes": [
            "managed_object",
            "next_check"
        ]
    }
    managed_object = ForeignKeyField(ManagedObject)
    last_check = DateTimeField(required=False)
    last_status = BooleanField(default=False)
    next_check = DateTimeField()

    @classmethod
    def reschedule(cls, object, ts, status=None):
        """
        Reschedule next interface check of object to time ts
        :param object: managed object
        :type object: ManagedObject
        :param ts: next check time
        :type ts: datetime.datetime
        """
        if isinstance(ts, int) or isinstance(ts, long):
            ts = datetime.datetime.now() + datetime.timedelta(seconds=ts)
        s = cls.objects.filter(managed_object=object.id).first()
        if s:
            s.next_check = ts
        else:
            s = cls(managed_object=object, next_check=ts)
        if status is not None:
            s.last_status = status
            s.last_check = datetime.datetime.now()
        s.save()


class NewPrefixDiscoveryLog(Document):
    meta = {
        "collection": "noc.log.discovery.prefix.new",
        "allow_inheritance": False,
        "indexes": ["-timestamp"]
    }
    timestamp = DateTimeField()
    vrf = StringField()
    prefix = StringField()
    description = StringField()
    managed_object = StringField()
    interface = StringField()

    def __unicode__(self):
        return "%s new %s:%s" % (self.timestamp, self.vrf, self.prefix)


class NewAddressDiscoveryLog(Document):
    meta = {
        "collection": "noc.log.discovery.address.new",
        "allow_inheritance": False,
        "indexes": ["-timestamp"]
    }
    timestamp = DateTimeField()
    vrf = StringField()
    address = StringField()
    description = StringField()
    managed_object = StringField()
    interface = StringField()

    def __unicode__(self):
        return "%s new %s:%s" % (self.timestamp, self.vrf, self.address)
