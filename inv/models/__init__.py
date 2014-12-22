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
from vendor import Vendor
from modelinterface import ModelInterface, ModelInterfaceAttr
from connectiontype import ConnectionType
from connectionrule import ConnectionRule
from objectmodel import ObjectModel
from unknownmodel import UnknownModel
from modelmapping import ModelMapping
from technology import Technology
from capability import Capability

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
from discoveryjob import DiscoveryJob


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
