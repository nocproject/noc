# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic config parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.facts.system import System
from noc.cm.facts.interface import Interface
from noc.cm.facts.subinterface import SubInterface
from noc.cm.facts.sysloghost import SyslogHost
from noc.cm.facts.ntpserver import NTPServer
from noc.cm.facts.user import User


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
        self.current_interface = None
        self.current_subinterface = None

    def parse(self, config):
        """
        Parse config, yield and modify facts
        """
        raise StopIteration

    def parse_file(self, path):
        with open(path) as f:
            for fact in self.parse(f.read()):
                yield fact

    def iter_facts(self):
        for f in self.pending_facts:
            yield f
        self.pending_facts = []

    def yield_fact(self, fact):
        self.pending_facts += [fact]

    def convert_interface_name(self, name):
        try:
            return self.managed_object.profile.convert_interface_name(name)
        except:
            return name

    def get_system_fact(self):
        if not self.system_fact:
            self.system_fact = System(
                profile=self.managed_object.profile_name,
                vendor=self.managed_object.get_attr("vendor"),
                platform=self.managed_object.get_attr("platform"),
                version=self.managed_object.get_attr("version")
            )
            self.yield_fact(self.system_fact)
        return self.system_fact

    def get_interface_defaults(self):
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
            self.interface_facts[n] = Interface(n, **self.get_interface_defaults())
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
