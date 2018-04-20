# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Basic config parser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Basic config parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.facts.system import System
from noc.cm.facts.interface import Interface
from noc.cm.facts.subinterface import SubInterface
from noc.cm.facts.sysloghost import SyslogHost
from noc.cm.facts.ntpserver import NTPServer
from noc.cm.facts.user import User
from noc.cm.facts.vlan import VLAN
from noc.cm.facts.service import Service
from noc.cm.facts.vrf import VRF
from noc.cm.facts.staticroute import StaticRoute


class BaseParser(object):
    def __init__(self, managed_object):
        self.managed_object = managed_object
        self.pending_facts = []
        self.system_fact = None
        self.interface_facts = {}
        self.subinterface_facts = {}
        self.sysloghost_facts = {}
        self.ntpserver_facts = {}
        self.user_facts = {}
        self.vlan_facts = {}
        self.service_facts = {}
        self.vrf_facts = {}
        self.current_interface = None
        self.current_subinterface = None
        self.current_vlan = None
        self.current_service = None
        self.current_vrf = None
        # Offsets of interface config sections
        # <interface name> -> [(start, end), .., (start, end)]
        self.interface_ranges = {}

    def parse(self, config):
        """
        Parse config, yield and modify facts
        """
        if False:
            yield  # Empty iterator

    def parse_file(self, path):
        with open(path) as f:
            for fact in self.parse(f.read()):
                yield fact

    def iter_facts(self):
        for f in self.pending_facts:
            f.managed_object = self.managed_object
            yield f
        self.pending_facts = []

    def yield_fact(self, fact):
        self.pending_facts += [fact]

    def convert_interface_name(self, name):
        try:
<<<<<<< HEAD
            return self.managed_object.get_profile().convert_interface_name(name)
        except Exception as e:
=======
            return self.managed_object.profile.convert_interface_name(name)
        except:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            return name

    def get_system_fact(self):
        if not self.system_fact:
            self.system_fact = System(
<<<<<<< HEAD
                profile=self.managed_object.profile.name,
                vendor=self.managed_object.vendor.code if self.managed_object.vendor else None,
                platform=self.managed_object.platform.name if self.managed_object.platform else None,
                version=self.managed_object.version.version if self.managed_object.version else None,
=======
                profile=self.managed_object.profile_name,
                vendor=self.managed_object.get_attr("vendor"),
                platform=self.managed_object.get_attr("platform"),
                version=self.managed_object.get_attr("version")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            )
            self.yield_fact(self.system_fact)
        return self.system_fact

    def get_interface_defaults(self, name):
        """
        Get interface default settings
        """
        return {}

    def get_subinterface_defaults(self):
        """
        Get subinterface default settings
        """
        return {}

    def get_user_defaults(self):
        """
        Get user default settings
        """
        return {}

    def get_interface_fact(self, name):
        n = self.convert_interface_name(name)
        if n not in self.interface_facts:
            self.interface_facts[n] = Interface(
                n, **self.get_interface_defaults(n)
            )
            self.yield_fact(self.interface_facts[n])
        self.current_interface = self.interface_facts[n]
        return self.current_interface

    def get_current_interface(self):
        """
        Returns last get_interface_fact call
        """
        return self.current_interface

    def get_subinterface_fact(self, name, interface_name=None):
        n = self.convert_interface_name(name)
        if n not in self.subinterface_facts:
            i_fact = self.get_interface_fact(
                self.convert_interface_name(
                    interface_name or name
                )
            )
            self.subinterface_facts[n] = SubInterface(
                n, interface=i_fact, **self.get_subinterface_defaults())
            self.yield_fact(self.subinterface_facts[n])
        self.current_subinterface = self.subinterface_facts[n]
        return self.current_subinterface

    def get_current_subinterface(self):
        """
        Returns last get_subinterface_fact call
        """
        return self.current_subinterface

    def get_sysloghost_fact(self, ip):
        if ip not in self.sysloghost_facts:
            self.sysloghost_facts[ip] = SyslogHost(ip)
            self.yield_fact(self.sysloghost_facts[ip])
        return self.sysloghost_facts[ip]

    def get_ntpserver_fact(self, ip):
        if ip not in self.ntpserver_facts:
            self.ntpserver_facts[ip] = NTPServer(ip)
            self.yield_fact(self.ntpserver_facts[ip])
        return self.ntpserver_facts[ip]

    def get_user_fact(self, name):
        if name not in self.user_facts:
            self.user_facts[name] = User(name, **self.get_user_defaults())
            self.yield_fact(self.user_facts[name])
        return self.user_facts[name]

    def get_vlan_fact(self, id):
        if id not in self.vlan_facts:
            self.vlan_facts[id] = VLAN(id)
            self.yield_fact(self.vlan_facts[id])
        self.current_vlan = self.vlan_facts[id]
        return self.current_vlan

    def get_current_vlan(self):
        """
        Returns last get_vlan_fact call
        """
        return self.current_vlan

    def get_service_fact(self, name):
        if name not in self.service_facts:
            self.service_facts[name] = Service(name)
            self.yield_fact(self.service_facts[name])
        self.current_service = self.service_facts[name]
        return self.current_service

    def get_current_service(self):
        """
        Returns last get_service_fact call
        """
        return self.current_service

    def get_vrf_fact(self, name):
        if name not in self.vrf_facts:
            self.vrf_facts[name] = VRF(name)
            self.yield_fact(self.vrf_facts[name])
        self.current_vrf = self.vrf_facts[name]
        return self.current_vrf

    def get_current_vrf(self):
        """
        Returns last get_vrf_fact call
        """
        return self.current_vrf

    def register_interface_section(self, name, start, end):
        """
        Register offsets of interface config section
        """
        name = self.convert_interface_name(name)
        if name in self.interface_ranges:
            self.interface_ranges[name] += [(start, end)]
        else:
            self.interface_ranges[name] = [(start, end)]

    def get_static_route_fact(self, prefix):
        f = StaticRoute(prefix=prefix)
        self.yield_fact(f)
<<<<<<< HEAD
        return f
=======
        return f
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
