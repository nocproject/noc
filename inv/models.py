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
## NOC modules
from noc.lib.nosql import *
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
        return u"%s: %s" % (self.managed_object.name, forwarding_instance)


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
    is_ignored = BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s: %s" % (self.managed_object.name, self.name)

    def save(self, *args, **kwargs):
        self.name = self.managed_object.profile.convert_interface_name(self.name)
        if self.mac:
            self.mac = MACAddressParameter().clean(self.mac)
        super(Interface, self).save(*args, **kwargs)

    @property
    def is_linked(self):
        """
        Check interface is linked
        :returns: True if interface is linked, False otherwise
        """
        return False  # @todo: Check Link


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
    """
    meta = {
        "collection": "noc.links",
        "allow_inheritance": False,
        "index": ["interfaces"]
    }

    interfaces = ListField(PlainReferenceField(Interface))

    def __unicode__(self):
        return u"(%s)" % ", ".join([unicode(i) for i in self.interfaces])


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
