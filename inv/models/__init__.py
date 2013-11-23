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


from vendor import Vendor
from modelinterface import ModelInterface, ModelInterfaceAttr
from connectiontype import ConnectionType
from connectionrule import ConnectionRule
from objectmodel import ObjectModel
from unknownmodel import UnknownModel
from modelmapping import ModelMapping


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
                    self.type.id == v.type.id and
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
from interfaceprofile import InterfaceProfile
from interfaceclassificationrule import InterfaceClassificationRule,\
    InterfaceClassificationMatch
from forwardinginstance import ForwardingInstance
from interface import Interface
from subinterface import SubInterface
from link import Link
from maclog import MACLog
from macdb import MACDB
from networkchart import NetworkChart


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
